"""Shared schema types."""

from pydantic import BaseModel


class ModelInfo(BaseModel):
    """Basic model metadata returned in all responses."""

    model: str


class ErrorDetail(BaseModel):
    """Single error detail item."""

    type: str
    message: str
    detail: list[object] = []
    request_id: str


class ErrorResponse(BaseModel):
    """Outer wrapper for all error responses."""

    error: ErrorDetail
