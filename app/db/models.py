"""SQLAlchemy ORM models."""

import uuid

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class RequestLog(Base):
    """Persisted record of every API request (best-effort)."""

    __tablename__ = "request_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    endpoint: Mapped[str] = mapped_column(String(32), nullable=False)
    request_body: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=True)
    response_summary: Mapped[dict[str, object]] = mapped_column(JSONB, nullable=True)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[object] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
