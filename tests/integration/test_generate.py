"""Integration tests: /api/v1/generate endpoint."""

from fastapi.testclient import TestClient


def test_generate_happy_path(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/generate",
        json={"prompt": "Once upon a time", "max_new_tokens": 10, "seed": 42},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "generated_text" in body
    assert "full_text" in body
    assert "num_prompt_tokens" in body
    assert "num_generated_tokens" in body
    assert "latency_ms" in body
    assert "params" in body
    assert body["params"]["seed"] == 42
    assert "model" in body


def test_generate_empty_prompt(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": ""})
    assert resp.status_code == 422


def test_generate_max_tokens_zero(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": "hi", "max_new_tokens": 0})
    assert resp.status_code == 422


def test_generate_bad_temperature(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": "hi", "temperature": 0.0})
    assert resp.status_code == 422


def test_generate_bad_top_p(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": "hi", "top_p": 1.5})
    assert resp.status_code == 422


def test_generate_negative_seed(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": "hi", "seed": -1})
    assert resp.status_code == 422


def test_generate_over_limit(client: TestClient) -> None:
    resp = client.post("/api/v1/generate", json={"prompt": "hi", "max_new_tokens": 9999})
    assert resp.status_code == 422
