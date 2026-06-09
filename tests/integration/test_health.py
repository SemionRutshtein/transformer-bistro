"""Integration tests: health endpoints."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_healthz(client: TestClient) -> None:
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_readyz_ready(client: TestClient) -> None:
    resp = client.get("/readyz")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ready"
    assert "model" in body


def test_readyz_not_ready() -> None:
    from app.main import app

    def _null_model(*_a: object, **_kw: object) -> None:
        app.state.model_service = None

    with (
        patch("app.main.ModelService", side_effect=_null_model),
        TestClient(app, raise_server_exceptions=False) as c,
    ):
        resp = c.get("/readyz")
    assert resp.status_code == 503
