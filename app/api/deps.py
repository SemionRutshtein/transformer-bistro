"""Dependency injection helpers."""

from typing import Annotated

from fastapi import Depends, Request

from app.core.errors import ModelNotReadyError
from app.services.model_service import AbstractModelService


def get_model_service(request: Request) -> AbstractModelService:
    """Return the shared model service; raise 503 if not yet loaded."""
    svc: AbstractModelService | None = request.app.state.model_service
    if svc is None:
        raise ModelNotReadyError()
    return svc


ModelServiceDep = Annotated[AbstractModelService, Depends(get_model_service)]
