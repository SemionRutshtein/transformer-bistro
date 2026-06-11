"""Encode and decode endpoints."""

import time

import anyio
from fastapi import APIRouter, BackgroundTasks

from app.api.deps import ModelServiceDep
from app.schemas.tokenize import DecodeRequest, DecodeResponse, EncodeRequest, EncodeResponse
from app.services import history_service

router = APIRouter(prefix="/api/v1", tags=["Tokenization"])


@router.post(
    "/encode",
    response_model=EncodeResponse,
    summary="Tokenize text into token IDs",
)
async def encode(
    body: EncodeRequest, svc: ModelServiceDep, background_tasks: BackgroundTasks
) -> EncodeResponse:
    """Convert input text to token IDs, token strings, and token count."""
    start = time.perf_counter()
    ids, tokens = await anyio.to_thread.run_sync(
        lambda: svc.encode(body.text, add_special_tokens=body.add_special_tokens)
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    resp = EncodeResponse(
        input_text=body.text,
        token_ids=ids,
        tokens=tokens,
        num_tokens=len(ids),
        model=svc.model_name,
    )
    background_tasks.add_task(
        history_service.record,
        endpoint="encode",
        request_body=body.model_dump(),
        response_summary={"num_tokens": resp.num_tokens},
        latency_ms=latency_ms,
        model=svc.model_name,
    )
    return resp


@router.post(
    "/decode",
    response_model=DecodeResponse,
    summary="Decode token IDs back to text",
)
async def decode(
    body: DecodeRequest, svc: ModelServiceDep, background_tasks: BackgroundTasks
) -> DecodeResponse:
    """Convert a list of token IDs to text. Raises 422 for out-of-vocabulary IDs."""
    start = time.perf_counter()
    text: str = await anyio.to_thread.run_sync(
        lambda: svc.decode(body.token_ids, skip_special_tokens=body.skip_special_tokens)
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    resp = DecodeResponse(token_ids=body.token_ids, text=text, model=svc.model_name)
    background_tasks.add_task(
        history_service.record,
        endpoint="decode",
        request_body=body.model_dump(),
        response_summary={"text_length": len(text)},
        latency_ms=latency_ms,
        model=svc.model_name,
    )
    return resp
