"""Generate endpoint."""

import asyncio
from typing import Any

import anyio
from fastapi import APIRouter

from app.api.deps import ModelServiceDep
from app.schemas.generate import GenerateParams, GenerateRequest, GenerateResponse
from app.services import history_service

router = APIRouter(prefix="/api/v1", tags=["Generation"])

_background_tasks: set[asyncio.Task[Any]] = set()


def _fire(coro: Any) -> None:
    task: asyncio.Task[Any] = asyncio.create_task(coro)
    _background_tasks.add(task)
    task.add_done_callback(_background_tasks.discard)


@router.post(
    "/generate",
    response_model=GenerateResponse,
    summary="Generate text from a prompt",
)
async def generate(body: GenerateRequest, svc: ModelServiceDep) -> GenerateResponse:
    """Run causal language model generation. CPU inference offloaded to thread pool."""
    generated_text, full_text, n_prompt, n_gen, latency_ms = await anyio.to_thread.run_sync(
        lambda: svc.generate(
            body.prompt,
            max_new_tokens=body.max_new_tokens,
            temperature=body.temperature,
            top_k=body.top_k,
            top_p=body.top_p,
            do_sample=body.do_sample,
            seed=body.seed,
        )
    )
    params = GenerateParams(
        max_new_tokens=body.max_new_tokens,
        temperature=body.temperature,
        top_k=body.top_k,
        top_p=body.top_p,
        do_sample=body.do_sample,
        seed=body.seed,
    )
    resp = GenerateResponse(
        prompt=body.prompt,
        generated_text=generated_text,
        full_text=full_text,
        num_prompt_tokens=n_prompt,
        num_generated_tokens=n_gen,
        params=params,
        model=svc.model_name,
        latency_ms=latency_ms,
    )
    _fire(
        history_service.record(
            endpoint="generate",
            request_body={
                "prompt": body.prompt[:200],
                "max_new_tokens": body.max_new_tokens,
                "seed": body.seed,
            },
            response_summary={
                "num_generated_tokens": n_gen,
                "latency_ms": latency_ms,
            },
            latency_ms=latency_ms,
            model=svc.model_name,
        )
    )
    return resp
