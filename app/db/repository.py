"""DB repository: read/write request logs."""

import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import RequestLog


async def insert_log(
    session: AsyncSession,
    *,
    endpoint: str,
    request_body: dict[str, object],
    response_summary: dict[str, object],
    latency_ms: int,
    model: str,
) -> RequestLog:
    log = RequestLog(
        id=uuid.uuid4(),
        endpoint=endpoint,
        request_body=request_body,
        response_summary=response_summary,
        latency_ms=latency_ms,
        model=model,
    )
    session.add(log)
    await session.commit()
    return log


async def fetch_recent(session: AsyncSession, *, limit: int = 20) -> list[RequestLog]:
    result = await session.execute(
        select(RequestLog).order_by(RequestLog.created_at.desc()).limit(limit)
    )
    return list(result.scalars().all())


def log_to_dict(log: RequestLog) -> dict[str, object]:
    return {
        "id": str(log.id),
        "endpoint": log.endpoint,
        "request_body": log.request_body,
        "response_summary": log.response_summary,
        "latency_ms": log.latency_ms,
        "model": log.model,
        "created_at": log.created_at.isoformat()
        if isinstance(log.created_at, datetime)
        else str(log.created_at),
    }
