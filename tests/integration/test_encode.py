"""Integration tests: /api/v1/encode endpoint."""

from fastapi.testclient import TestClient


def test_encode_happy_path(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": "Hello world"})
    assert resp.status_code == 200
    body = resp.json()
    assert "token_ids" in body
    assert "tokens" in body
    assert "num_tokens" in body
    assert body["num_tokens"] == len(body["token_ids"])
    assert body["input_text"] == "Hello world"
    assert "model" in body


def test_encode_empty_text(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": ""})
    assert resp.status_code == 422
    assert resp.json()["error"]["type"] == "validation_error"


def test_encode_whitespace_only(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": "   "})
    assert resp.status_code == 422


def test_encode_text_too_long(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": "x" * 10_001})
    assert resp.status_code == 422


def test_encode_missing_text(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={})
    assert resp.status_code == 422


def test_encode_add_special_tokens(client: TestClient) -> None:
    resp = client.post("/api/v1/encode", json={"text": "hello", "add_special_tokens": True})
    assert resp.status_code == 200
