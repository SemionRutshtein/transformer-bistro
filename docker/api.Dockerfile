# ── builder stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

ARG MODEL_NAME=gpt2

ENV POETRY_VERSION=2.4.1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_HOME="/opt/poetry" \
    HF_HOME=/models \
    PYTHONDONTWRITEBYTECODE=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}"

WORKDIR /app
COPY pyproject.toml poetry.lock* ./

# Install main deps via poetry
RUN poetry install --only main --no-root

# torch is not in poetry.lock (explicit custom source); install directly into the venv
RUN .venv/bin/pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Bake the model weights into the image for offline / fast cold start
COPY app/ ./app/
RUN .venv/bin/python -c "\
from transformers import AutoModelForCausalLM, AutoTokenizer; \
AutoTokenizer.from_pretrained('${MODEL_NAME}'); \
AutoModelForCausalLM.from_pretrained('${MODEL_NAME}')"


# ── runtime stage ─────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

ENV HF_HOME=/models \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    HF_HUB_OFFLINE=1 \
    TRANSFORMERS_OFFLINE=1 \
    HF_DATASETS_OFFLINE=1

# Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app
COPY --from=builder /app/.venv ./.venv
COPY --from=builder /models /models
COPY app/ ./app/

RUN chown -R appuser:appuser /app /models
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"

# PORT env var is injected by Railway; falls back to 8000 for local/docker-compose
CMD uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
