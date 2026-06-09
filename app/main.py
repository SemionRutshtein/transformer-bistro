"""FastAPI application factory."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.errors import (
    InvalidTokenError,
    ModelNotReadyError,
    internal_error_handler,
    invalid_token_handler,
    model_not_ready_handler,
    not_found_handler,
    validation_exception_handler,
)
from app.core.logging import RequestIDMiddleware, configure_logging
from app.db.session import close_db, init_db
from app.services.model_service import ModelService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Load model and DB at startup; tear down on shutdown."""
    configure_logging(settings.log_level)
    logger.info("Starting up — loading model: %s", settings.model_name)
    app.state.model_service = None
    await init_db()
    # Load model synchronously (CPU, fits in startup time budget)
    app.state.model_service = ModelService(settings.model_name)
    logger.info("Model ready.")
    yield
    logger.info("Shutting down.")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Transformer Bistro",
        version="0.1.0",
        description=(
            "REST API serving a small open-source LLM. "
            "Endpoints: /api/v1/encode, /api/v1/decode, /api/v1/generate, /api/v1/history."
        ),
        lifespan=lifespan,
    )

    # Middlewares
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception handlers
    app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(InvalidTokenError, invalid_token_handler)  # type: ignore[arg-type]
    app.add_exception_handler(ModelNotReadyError, model_not_ready_handler)  # type: ignore[arg-type]
    app.add_exception_handler(404, not_found_handler)
    app.add_exception_handler(Exception, internal_error_handler)

    # Routes
    from app.api.routes import generate, health, history, tokenize

    app.include_router(health.router)
    app.include_router(tokenize.router)
    app.include_router(generate.router)
    app.include_router(history.router)

    return app


app = create_app()
