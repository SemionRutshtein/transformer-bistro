"""Shared test fixtures."""

from collections.abc import Generator
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.services.model_service import AbstractModelService

FAKE_VOCAB_SIZE = 50257
FAKE_MODEL_NAME = "gpt2-fake"


class FakeModelService(AbstractModelService):
    """Deterministic stub for unit/integration tests — no model download."""

    @property
    def model_name(self) -> str:
        return FAKE_MODEL_NAME

    @property
    def vocab_size(self) -> int:
        return FAKE_VOCAB_SIZE

    def encode(self, text: str, *, add_special_tokens: bool = False) -> tuple[list[int], list[str]]:
        # Deterministic: one token per word
        words = text.split()
        ids = [hash(w) % FAKE_VOCAB_SIZE for w in words]
        tokens = words
        return ids, tokens

    def decode(self, token_ids: list[int], *, skip_special_tokens: bool = True) -> str:
        from app.core.errors import InvalidTokenError

        bad = [tid for tid in token_ids if not (0 <= tid < FAKE_VOCAB_SIZE)]
        if bad:
            raise InvalidTokenError(bad, FAKE_VOCAB_SIZE)
        return " ".join(str(tid) for tid in token_ids)

    def generate(
        self,
        prompt: str,
        *,
        max_new_tokens: int = 50,
        temperature: float = 1.0,
        top_k: int = 50,
        top_p: float = 0.95,
        do_sample: bool = True,
        seed: int | None = None,
    ) -> tuple[str, str, int, int, int]:
        generated = "fake generated text"
        full = f"{prompt} {generated}"
        n_prompt = len(prompt.split())
        n_gen = len(generated.split())
        return generated, full, n_prompt, n_gen, 42


@pytest.fixture
def fake_svc() -> FakeModelService:
    return FakeModelService()


@pytest.fixture
def client(fake_svc: FakeModelService) -> Generator[TestClient, None, None]:
    """TestClient with the real app but FakeModelService injected via mock."""
    from app.main import app

    # Patch ModelService so the lifespan doesn't download the real model.
    with (
        patch("app.main.ModelService", return_value=fake_svc),
        TestClient(app, raise_server_exceptions=False) as c,
    ):
        yield c
