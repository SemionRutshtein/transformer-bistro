# Transformer Bistro

A Dockerized REST API that serves a small open-source LLM (GPT-2 by default) with tokenization and text generation endpoints, a PostgreSQL request history store, and a React frontend.

```
┌───────────────┐     /api/v1/*     ┌─────────────────┐
│  React UI     │ ───────────────▶  │  FastAPI (8000) │
│  (nginx :80)  │                   │  + uvicorn      │
└───────────────┘                   └────────┬────────┘
                                             │
                                    ┌────────┴────────┐
                                    │  GPT-2 weights  │
                                    │  (HF cache)     │
                                    └────────┬────────┘
                                             │ async
                                    ┌────────▼────────┐
                                    │  PostgreSQL 16  │
                                    │  (request logs) │
                                    └─────────────────┘
```

---

## Assumptions

1. **Model:** GPT-2 (124 M params, ~500 MB). CPU-only, no GPU assumed. Configurable via `MODEL_NAME` env var — swap in `EleutherAI/gpt-neo-125m` with zero code changes.
2. **CPU-only inference.** The CPU torch wheel is installed to keep image size down and avoid CUDA dependencies.
3. **Single model instance, loaded once** via FastAPI `lifespan`. Model weights are baked into the Docker image for offline and fast cold starts.
4. **One uvicorn worker.** Each worker loads its own model copy; single worker is correct and memory-efficient for a demo. Horizontal scaling path: put a reverse proxy (nginx/Envoy) in front and run multiple single-worker containers.
5. **GPT-2 has no pad token.** Set to `eos_token` at load time.
6. **DB is optional at runtime.** If unreachable or disabled, the three core endpoints still work and history writes are silently swallowed and logged.

---

## Prerequisites

- Docker Desktop (for `docker compose` path)
- OR Python 3.12 + Poetry 2.x + Node 20 (for local dev)

---

## Quickstart

```bash
# 1. Copy env
cp .env.example .env

# 2. Start the full stack (db + api + frontend)
docker compose up --build
```

- API + Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:3000
- Health: http://localhost:8000/healthz
- Ready: http://localhost:8000/readyz

The first build bakes GPT-2 weights into the image (~1.5 GB); subsequent builds use cache.

---

## API Reference

Base path: `/api/v1`. All bodies and responses are JSON.

### `POST /api/v1/encode`
```bash
curl -s localhost:8000/api/v1/encode \
  -H 'Content-Type: application/json' \
  -d '{"text":"Hello world"}'
```
Response:
```json
{
  "input_text": "Hello world",
  "token_ids": [15496, 995],
  "tokens": ["Hello", " world"],
  "num_tokens": 2,
  "model": "gpt2"
}
```

### `POST /api/v1/decode`
```bash
curl -s localhost:8000/api/v1/decode \
  -H 'Content-Type: application/json' \
  -d '{"token_ids":[15496,995]}'
```
Response:
```json
{ "token_ids": [15496, 995], "text": "Hello world", "model": "gpt2" }
```

### `POST /api/v1/generate`
```bash
curl -s localhost:8000/api/v1/generate \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"Once upon a time","max_new_tokens":40,"seed":42}'
```
Response:
```json
{
  "prompt": "Once upon a time",
  "generated_text": " there was ...",
  "full_text": "Once upon a time there was ...",
  "num_prompt_tokens": 4,
  "num_generated_tokens": 40,
  "params": { "max_new_tokens": 40, "seed": 42, "..." : "..." },
  "model": "gpt2",
  "latency_ms": 812
}
```

### `GET /api/v1/history?limit=20`
Returns the most recent persisted requests (up to 100). Returns `[]` if DB is disabled.

Full auto-generated docs: http://localhost:8000/docs

---

## Configuration

| Env var              | Default                            | Description |
|----------------------|------------------------------------|-------------|
| `MODEL_NAME`         | `gpt2`                             | HuggingFace model id |
| `HF_HOME`            | `/models`                          | Cache dir (baked into image) |
| `MAX_INPUT_CHARS`    | `10000`                            | Encode text character limit |
| `MAX_TOKEN_IDS`      | `4096`                             | Decode list length limit |
| `MAX_NEW_TOKENS_LIMIT` | `512`                            | Generate hard cap |
| `DATABASE_URL`       | `postgresql+asyncpg://...`         | Leave empty to disable history |
| `ENABLE_HISTORY`     | `true`                             | Toggle DB persistence |
| `LOG_LEVEL`          | `INFO`                             | Logging level |
| `CORS_ORIGINS`       | `http://localhost:5173,...`        | Allowed CORS origins |

---

## Running Tests, Coverage, Linting

```bash
# Install dependencies
poetry install
# Install CPU torch (not on PyPI default index)
.venv/bin/pip install torch --index-url https://download.pytorch.org/whl/cpu

# Fast test suite (no model download; uses FakeModelService)
make test

# Coverage report (HTML + terminal)
make cov

# Real-model tests (requires ~500 MB download)
make slow

# Lint + format check
make lint

# Type check (mypy strict)
make type
```

---

## Design Decisions & Trade-offs

| Decision | Choice | Trade-off |
|----------|--------|-----------|
| Model | GPT-2 (124 M) | Smaller than GPT-Neo-125M, downloads faster, identical API |
| Inference | CPU-only | No CUDA required; slower than GPU |
| Workers | Single uvicorn | No per-worker memory duplication; scale with containers |
| Model loading | Baked into image | Faster cold start, ~1.5 GB image vs. ~200 MB + volume mount |
| History | Best-effort async | Core endpoints never fail due to DB issues |
| Testability | DI + FakeModelService | Full API test suite runs in <1s, no model download in CI |
| Async routes | `anyio.to_thread.run_sync` | CPU work leaves event loop free for other requests |
| Error format | Consistent envelope | All 4xx/5xx include `type`, `message`, `detail`, `request_id` |

---

## Project Structure

```
app/
├── main.py              # App factory + lifespan (model load, DB init)
├── config.py            # pydantic-settings env config
├── api/
│   ├── deps.py          # DI: get_model_service
│   └── routes/          # health, tokenize, generate, history
├── schemas/             # Pydantic request/response models
├── services/            # ModelService, history_service
├── db/                  # SQLAlchemy async engine, ORM, repository
└── core/                # errors, logging middleware
tests/
├── conftest.py          # FakeModelService, client fixture
├── unit/                # schema validation, error handlers, service units
└── integration/         # HTTP endpoint tests (no model download)
frontend/
├── src/
│   ├── api.ts           # Typed fetch wrappers
│   └── components/      # Encode, Decode, Generate, History panels
└── nginx.conf           # Proxy /api → api:8000
docker/
├── api.Dockerfile       # Multi-stage; bakes model weights
└── frontend.Dockerfile  # Vite build → nginx
```

---

## Possible Improvements

- **Streaming** via SSE for long generations (`EventSourceResponse`)
- **Batching / queuing** with a task queue (Celery / ARQ) for concurrent requests
- **GPU path**: add `device_map="auto"` and a GPU-enabled base image
- **Multiple workers**: gunicorn + multiple uvicorn workers with a shared model loaded via a sidecar/proxy
- **Alembic migrations** instead of `create_all` at startup
- **Auth + rate limiting**: API key middleware, per-key limits
- **Model warm-pool**: pre-load multiple model variants and switch by request header
