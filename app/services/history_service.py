"""Best-effort request history persistence."""

import logging

from app.db.repository import insert_log
from app.db.session import get_session_factory

logger = logging.getLogger(__name__)


async def record(
    *,
    endpoint: str,
    request_body: dict[str, object],
    response_summary: dict[str, object],
    latency_ms: int,
    model: str,
) -> None:
    """Persist a request log. Silently swallows all errors so callers are unaffected."""
    factory = get_session_factory()
    if factory is None:
        return
    try:
        async with factory() as session:
            await insert_log(
                session,
                endpoint=endpoint,
                request_body=request_body,
                response_summary=response_summary,
                latency_ms=latency_ms,
                model=model,
            )
    except Exception as exc:
        logger.warning("History write failed (non-fatal): %s", exc)
