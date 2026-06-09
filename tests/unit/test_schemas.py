"""Unit tests: Pydantic schema validation boundaries."""

import pytest
from pydantic import ValidationError

from app.schemas.generate import GenerateRequest
from app.schemas.tokenize import DecodeRequest, EncodeRequest


class TestEncodeRequest:
    def test_valid(self) -> None:
        req = EncodeRequest(text="hello world")
        assert req.text == "hello world"

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationError, match="empty"):
            EncodeRequest(text="")

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(ValidationError, match="empty"):
            EncodeRequest(text="   ")

    def test_too_long_raises(self) -> None:
        with pytest.raises(ValidationError, match="max length"):
            EncodeRequest(text="x" * 10_001)

    def test_add_special_tokens_default_false(self) -> None:
        req = EncodeRequest(text="hi")
        assert req.add_special_tokens is False


class TestDecodeRequest:
    def test_valid(self) -> None:
        req = DecodeRequest(token_ids=[1, 2, 3])
        assert req.token_ids == [1, 2, 3]

    def test_empty_raises(self) -> None:
        with pytest.raises(ValidationError, match="empty"):
            DecodeRequest(token_ids=[])

    def test_too_many_raises(self) -> None:
        with pytest.raises(ValidationError, match="maximum"):
            DecodeRequest(token_ids=list(range(4_097)))

    def test_non_int_raises(self) -> None:
        with pytest.raises(ValidationError):
            DecodeRequest(token_ids=["a", "b"])  # type: ignore[list-item]


class TestGenerateRequest:
    def test_valid_defaults(self) -> None:
        req = GenerateRequest(prompt="hello")
        assert req.max_new_tokens == 50
        assert req.temperature == 1.0
        assert req.do_sample is True

    def test_empty_prompt_raises(self) -> None:
        with pytest.raises(ValidationError, match="empty"):
            GenerateRequest(prompt="")

    def test_max_new_tokens_below_1_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", max_new_tokens=0)

    def test_temperature_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", temperature=0.0)

    def test_temperature_above_2_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", temperature=2.1)

    def test_top_p_above_1_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", top_p=1.1)

    def test_top_p_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", top_p=0.0)

    def test_negative_seed_raises(self) -> None:
        with pytest.raises(ValidationError):
            GenerateRequest(prompt="hi", seed=-1)

    def test_max_new_tokens_exceeds_server_limit(self) -> None:
        with pytest.raises(ValidationError, match="server limit"):
            GenerateRequest(prompt="hi", max_new_tokens=9999)
