"""Request history endpoint."""

from fastapi import APIRouter, Query

from app.db.repository import fetch_recent, log_to_dict
from app.db.session import get_session_factory

router = APIRouter(prefix="/api/v1", tags=["History"])


@router.get("/history", summary="List recent API requests")
async def get_history(
    limit: int = Query(20, ge=1, le=100, description="Max records to return."),
) -> list[dict[str, object]]:
    """Return the most recent persisted requests. Returns [] if history is disabled."""
    factory = get_session_factory()
    if factory is None:
        return []
    async with factory() as session:
        logs = await fetch_recent(session, limit=limit)
    return [log_to_dict(log) for log in logs]
