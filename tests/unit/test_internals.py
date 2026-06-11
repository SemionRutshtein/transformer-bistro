"""Unit tests for internal services, DB layer, and error handlers."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from app.schemas.common import ErrorDetail, ErrorResponse, ModelInfo
from app.schemas.generate import GenerateParams, GenerateRequest, GenerateResponse

# ── schemas/common.py ─────────────────────────────────────────────────────────


class TestCommonSchemas:
    def test_model_info(self) -> None:
        m = ModelInfo(model="gpt2")
        assert m.model == "gpt2"

    def test_error_detail(self) -> None:
        d = ErrorDetail(type="foo", message="bar", request_id="x")
        assert d.type == "foo"
        assert d.detail == []

    def test_error_response(self) -> None:
        r = ErrorResponse(error=ErrorDetail(type="t", message="m", request_id="r"))
        assert r.error.type == "t"


# ── schemas/generate.py ───────────────────────────────────────────────────────


class TestGenerateSchemaExtra:
    def test_prompt_too_long(self) -> None:
        with pytest.raises(ValidationError, match="4000"):
            GenerateRequest(prompt="x" * 4_001)

    def test_generate_params(self) -> None:
        p = GenerateParams(
            max_new_tokens=10,
            temperature=1.0,
            top_k=50,
            top_p=0.9,
            do_sample=True,
            seed=None,
        )
        assert p.seed is None

    def test_generate_response(self) -> None:
        r = GenerateResponse(
            prompt="hi",
            generated_text="world",
            full_text="hi world",
            num_prompt_tokens=1,
            num_generated_tokens=1,
            params=GenerateParams(
                max_new_tokens=10,
                temperature=1.0,
                top_k=50,
                top_p=0.9,
                do_sample=True,
                seed=1,
            ),
            model="gpt2",
            latency_ms=100,
        )
        assert r.latency_ms == 100


# ── core/errors.py — internal_error_handler ──────────────────────────────────


def test_internal_error_handler_called() -> None:
    """Directly invoke internal_error_handler to exercise lines 89-91."""
    import json

    from starlette.requests import Request as SRequest

    from app.core.errors import internal_error_handler

    async def _run() -> None:
        scope: dict[str, object] = {"type": "http", "state": {"request_id": "test-id"}}
        req = SRequest(scope)  # type: ignore[arg-type]
        exc = RuntimeError("test error")
        resp = await internal_error_handler(req, exc)
        assert resp.status_code == 500
        body = json.loads(resp.body)
        assert body["error"]["type"] == "internal_error"

    asyncio.run(_run())


# ── services/history_service.py ───────────────────────────────────────────────


class TestHistoryService:
    def test_record_no_factory(self) -> None:
        """record() with no session factory returns silently."""
        from app.services import history_service

        with patch("app.services.history_service.get_session_factory", return_value=None):
            asyncio.run(
                history_service.record(
                    endpoint="encode",
                    request_body={},
                    response_summary={},
                    latency_ms=0,
                    model="gpt2",
                )
            )

    def test_record_db_error_silenced(self) -> None:
        """DB write failure is swallowed silently."""
        from app.services import history_service

        mock_session = AsyncMock()
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)
        mock_factory = MagicMock(return_value=mock_session)

        with (
            patch(
                "app.services.history_service.get_session_factory",
                return_value=mock_factory,
            ),
            patch(
                "app.services.history_service.insert_log",
                side_effect=RuntimeError("db error"),
            ),
        ):
            asyncio.run(
                history_service.record(
                    endpoint="encode",
                    request_body={},
                    response_summary={},
                    latency_ms=0,
                    model="gpt2",
                )
            )
        # No exception = success


# ── db/session.py ─────────────────────────────────────────────────────────────


class TestDbSession:
    def test_init_db_no_url(self) -> None:
        from app.db import session as db_session

        with patch.object(db_session.settings, "database_url", ""):
            result = asyncio.run(db_session.init_db())
        assert result is False

    def test_init_db_disabled(self) -> None:
        from app.db import session as db_session

        with (
            patch.object(db_session.settings, "database_url", "postgresql://x"),
            patch.object(db_session.settings, "enable_history", False),
        ):
            result = asyncio.run(db_session.init_db())
        assert result is False

    def test_init_db_connection_failure(self) -> None:
        from app.db import session as db_session

        with (
            patch.object(db_session.settings, "database_url", "postgresql+asyncpg://bad/db"),
            patch.object(db_session.settings, "enable_history", True),
            patch("app.db.session.create_async_engine", side_effect=Exception("fail")),
        ):
            result = asyncio.run(db_session.init_db())
        assert result is False

    def test_close_db_none(self) -> None:
        from app.db import session as db_session

        db_session._engine = None
        asyncio.run(db_session.close_db())
