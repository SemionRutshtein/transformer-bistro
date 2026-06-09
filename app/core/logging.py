"""Structured logging setup and request-id pure ASGI middleware."""

import logging
import uuid

from fastapi import Request
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

REQUEST_ID_CTX_KEY = "request_id"


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with structured format."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s %(message)s",
    )
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("torch").setLevel(logging.WARNING)


class RequestIDMiddleware:
    """Pure ASGI middleware: attaches a UUID request_id to every request.

    Uses pure ASGI (not BaseHTTPMiddleware) to avoid exception-propagation issues
    that affect Starlette's BaseHTTPMiddleware in recent versions.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        request_id = str(uuid.uuid4())
        # Attach to scope state so route handlers can read it via request.state
        if "state" not in scope:
            scope["state"] = {}
        scope["state"][REQUEST_ID_CTX_KEY] = request_id

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                headers.append("X-Request-ID", request_id)
            await send(message)

        await self.app(scope, receive, send_with_id)


def get_request_id(request: Request) -> str:
    """Extract request_id from request state, falling back to a new UUID."""
    return getattr(request.state, REQUEST_ID_CTX_KEY, str(uuid.uuid4()))
