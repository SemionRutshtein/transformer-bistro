"""Integration tests: /api/v1/history endpoint."""

from fastapi.testclient import TestClient


def test_history_returns_list(client: TestClient) -> None:
    resp = client.get("/api/v1/history")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_history_limit_validation(client: TestClient) -> None:
    resp = client.get("/api/v1/history?limit=0")
    assert resp.status_code == 422


def test_history_limit_too_high(client: TestClient) -> None:
    resp = client.get("/api/v1/history?limit=101")
    assert resp.status_code == 422


def test_history_default_limit(client: TestClient) -> None:
    resp = client.get("/api/v1/history")
    assert resp.status_code == 200
