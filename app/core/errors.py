"""Domain exceptions and FastAPI exception handlers."""

import logging
import traceback

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.logging import get_request_id

logger = logging.getLogger(__name__)


class InvalidTokenError(Exception):
    """Raised when token IDs outside the model's vocabulary are submitted."""

    def __init__(self, bad_ids: list[int], vocab_size: int) -> None:
        self.bad_ids = bad_ids
        self.vocab_size = vocab_size
        super().__init__(f"Invalid token ids {bad_ids}; valid range [0, {vocab_size})")


class ModelNotReadyError(Exception):
    """Raised when a request arrives before the model has finished loading."""


def _error_body(
    error_type: str,
    message: str,
    request_id: str,
    detail: list[object] | None = None,
) -> dict[str, object]:
    return {
        "error": {
            "type": error_type,
            "message": message,
            "detail": detail or [],
            "request_id": request_id,
        }
    }


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(
            "validation_error",
            "Request validation failed.",
            request_id,
            jsonable_encoder(exc.errors()),
        ),
    )


async def invalid_token_handler(request: Request, exc: InvalidTokenError) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_body(
            "invalid_token",
            f"Token ids {exc.bad_ids} are out of vocabulary range [0, {exc.vocab_size}).",
            request_id,
        ),
    )


async def model_not_ready_handler(request: Request, exc: ModelNotReadyError) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=_error_body("service_unavailable", "Model is not ready yet.", request_id),
    )


async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=_error_body("not_found", "The requested resource was not found.", request_id),
    )


async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    request_id = get_request_id(request)
    logger.error("Unhandled exception request_id=%s\n%s", request_id, traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_body("internal_error", "An unexpected error occurred.", request_id),
    )
