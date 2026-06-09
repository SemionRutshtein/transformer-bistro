"""Async SQLAlchemy engine and session factory."""

import logging

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.db.models import Base

logger = logging.getLogger(__name__)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine | None:
    return _engine


async def init_db() -> bool:
    """Create engine + tables. Returns True on success, False if DB is unavailable."""
    global _engine, _session_factory

    if not settings.database_url or not settings.enable_history:
        logger.info("History disabled (no DATABASE_URL or ENABLE_HISTORY=false).")
        return False

    try:
        _engine = create_async_engine(settings.database_url, echo=False, pool_pre_ping=True)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
        async with _engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database connected and tables ready.")
        return True
    except Exception as exc:
        logger.warning("DB init failed (history disabled): %s", exc)
        _engine = None
        _session_factory = None
        return False


async def close_db() -> None:
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None


def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    return _session_factory
