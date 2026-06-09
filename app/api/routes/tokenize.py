"""Encode and decode endpoints."""

import asyncio
from typing import Any

import anyio
from fastapi import APIRouter

from app.api.deps import ModelServiceDep
from app.schemas.tokenize import DecodeRequest, DecodeResponse, EncodeRequest, EncodeResponse
from app.services import history_service

router = APIRouter(prefix="/api/v1", tags=["Tokenization"])

# Keeps task references alive until completion (prevents GC of fire-and-forget tasks).
_background_tasks: set[asyncio.Task[Any]] = set()


def _fire(coro: Any) -> None:
    task: asyncio.Task[Any] = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


@router.post(
    "/encode",
    response_model=EncodeResponse,
    summary="Tokenize text into token IDs",
)
async def encode(body: EncodeRequest, svc: ModelServiceDep) -> EncodeResponse:
    """Convert input text to token IDs, token strings, and token count."""
    ids, tokens = await anyio.to_thread.run_sync(
        lambda: svc.encode(body.text, add_special_tokens=body.add_special_tokens)
    )
    resp = EncodeResponse(
        input_text=body.text,
        token_ids=ids,
        tokens=tokens,
        num_tokens=len(ids),
        model=svc.model_name,
    )
    _fire(
        history_service.record(
            endpoint="encode",
            request_body=body.model_dump(),
            response_summary={"num_tokens": resp.num_tokens},
            latency_ms=0,
            model=svc.model_name,
        )
    )
    return resp


@router.post(
    "/decode",
    response_model=DecodeResponse,
    summary="Decode token IDs back to text",
)
async def decode(body: DecodeRequest, svc: ModelServiceDep) -> DecodeResponse:
    """Convert a list of token IDs to text. Raises 422 for out-of-vocabulary IDs."""
    text: str = await anyio.to_thread.run_sync(
        lambda: svc.decode(body.token_ids, skip_special_tokens=body.skip_special_tokens)
    )
    resp = DecodeResponse(token_ids=body.token_ids, text=text, model=svc.model_name)
    _fire(
        history_service.record(
            endpoint="decode",
            request_body=body.model_dump(),
            response_summary={"text_length": len(text)},
            latency_ms=0,
            model=svc.model_name,
        )
    )
    return resp
