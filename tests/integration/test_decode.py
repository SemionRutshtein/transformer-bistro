"""Integration tests: /api/v1/decode endpoint."""

from fastapi.testclient import TestClient


def test_decode_happy_path(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": [1, 2, 3]})
    assert resp.status_code == 200
    body = resp.json()
    assert "text" in body
    assert body["token_ids"] == [1, 2, 3]
    assert "model" in body


def test_decode_empty_ids(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": []})
    assert resp.status_code == 422
    assert resp.json()["error"]["type"] == "validation_error"


def test_decode_out_of_vocab(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": [99999999]})
    assert resp.status_code == 422
    assert resp.json()["error"]["type"] == "invalid_token"


def test_decode_non_int_ids(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": ["abc"]})
    assert resp.status_code == 422


def test_decode_too_many_ids(client: TestClient) -> None:
    resp = client.post("/api/v1/decode", json={"token_ids": list(range(4_097))})
    assert resp.status_code == 422
