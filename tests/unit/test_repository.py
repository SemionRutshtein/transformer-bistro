"""Unit tests for the database repository layer."""

import asyncio
import uuid
from unittest.mock import AsyncMock, MagicMock

from app.db.models import RequestLog
from app.db.repository import fetch_recent, insert_log, log_to_dict


def test_log_to_dict_str_created_at() -> None:
    """log_to_dict handles non-datetime created_at gracefully."""
    log = RequestLog(
        id=uuid.uuid4(),
        endpoint="encode",
        request_body={"text": "hi"},
        response_summary={"num_tokens": 2},
        latency_ms=10,
        model="gpt2",
        created_at="2024-01-01T00:00:00",
    )
    d = log_to_dict(log)
    assert d["endpoint"] == "encode"
    assert d["model"] == "gpt2"
    assert isinstance(d["id"], str)


def test_insert_log_adds_and_commits() -> None:
    """insert_log adds a RequestLog to the session and commits."""
    session = AsyncMock()
    session.add = MagicMock()

    log = asyncio.run(
        insert_log(
            session,
            endpoint="decode",
            request_body={"token_ids": [1]},
            response_summary={"text_length": 5},
            latency_ms=7,
            model="gpt2",
        )
    )
    session.add.assert_called_once_with(log)
    session.commit.assert_awaited_once()
    assert log.endpoint == "decode"
    assert log.latency_ms == 7


def test_fetch_recent_returns_logs() -> None:
    """fetch_recent returns the scalar results of the select query."""
    expected = [MagicMock(spec=RequestLog), MagicMock(spec=RequestLog)]
    result = MagicMock()
    result.scalars.return_value.all.return_value = expected
    session = AsyncMock()
    session.execute = AsyncMock(return_value=result)

    logs = asyncio.run(fetch_recent(session, limit=2))
    assert logs == expected
    session.execute.assert_awaited_once()
