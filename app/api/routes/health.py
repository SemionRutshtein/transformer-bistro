"""Health and readiness probe endpoints."""

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Health"])


@router.get("/healthz", summary="Liveness probe")
async def healthz() -> dict[str, str]:
    """Always returns 200. Indicates the process is alive."""
    return {"status": "ok"}


@router.get("/readyz", summary="Readiness probe")
async def readyz(request: Request) -> JSONResponse:
    """Returns 200 once the model is loaded; 503 while loading."""
    svc = request.app.state.model_service
    if svc is None:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "loading"},
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "ready", "model": svc.model_name},
    )
