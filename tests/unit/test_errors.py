"""Unit tests: exception handlers return correct status + envelope."""

from unittest.mock import patch

from fastapi.testclient import TestClient


def test_validation_error_envelope(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": ""})
    assert resp.status_code == 422
    body = resp.json()
    assert "error" in body
    assert body["error"]["type"] == "validation_error"
    assert "request_id" in body["error"]


def test_invalid_token_envelope(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": [99999999]})
    assert resp.status_code == 422
    body = resp.json()
    assert body["error"]["type"] == "invalid_token"
    assert "request_id" in body["error"]


def test_not_found_envelope(client: TestClient) -> None:
    resp = client.get("/api/v1/nonexistent")
    assert resp.status_code == 404


def test_model_not_ready() -> None:
    from app.main import app

    def _null_model(*_a: object, **_kw: object) -> None:
        app.state.model_service = None

    with (
        patch("app.main.ModelService", side_effect=_null_model),
        TestClient(app, raise_server_exceptions=False) as c,
    ):
        resp = c.post("/api/v1/encode", json={"text": "hello"})
    assert resp.status_code == 503


def test_request_id_header(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": "hello"})
    assert "x-request-id" in resp.headers
