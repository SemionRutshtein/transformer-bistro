"""Slow unit tests: real GPT-2 model (require local download)."""

import pytest

pytestmark = pytest.mark.slow


@pytest.fixture(scope="module")
def real_svc():  # type: ignore[no-untyped-def]
    from app.services.model_service import ModelService

    return ModelService("gpt2")


def test_encode_decode_roundtrip(real_svc) -> None:  # type: ignore[no-untyped-def]
    text = "Hello world"
    ids, _tokens = real_svc.encode(text)
    decoded = real_svc.decode(ids)
    assert decoded.strip() == text


def test_encode_returns_types(real_svc) -> None:  # type: ignore[no-untyped-def]
    ids, tokens = real_svc.encode("Hello world")
    assert isinstance(ids, list)
    assert all(isinstance(i, int) for i in ids)
    assert isinstance(tokens, list)
    assert len(ids) == len(tokens)
    assert len(ids) > 0


def test_decode_bad_ids_raises(real_svc) -> None:  # type: ignore[no-untyped-def]
    from app.core.errors import InvalidTokenError

    with pytest.raises(InvalidTokenError):
        real_svc.decode([999_999_999])


def test_generate_prefix_match(real_svc) -> None:  # type: ignore[no-untyped-def]
    prompt = "Once upon a time"
    _, full_text, n_prompt, n_gen, latency_ms = real_svc.generate(
        prompt, max_new_tokens=10, seed=42
    )
    assert full_text.startswith(prompt)
    assert n_gen == 10
    assert n_prompt > 0
    assert latency_ms >= 0


def test_generate_deterministic_with_seed(real_svc) -> None:  # type: ignore[no-untyped-def]
    prompt = "The quick brown fox"
    gen1, _, _, _, _ = real_svc.generate(prompt, max_new_tokens=5, seed=0)
    gen2, _, _, _, _ = real_svc.generate(prompt, max_new_tokens=5, seed=0)
    assert gen1 == gen2


def test_vocab_size(real_svc) -> None:  # type: ignore[no-untyped-def]
    assert real_svc.vocab_size == 50257
