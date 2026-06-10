"""Model service: wraps HuggingFace tokenizer + causal LM."""

import logging
import time
from abc import ABC, abstractmethod
from typing import cast

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer

from app.config import settings
from app.core.errors import InvalidTokenError

logger = logging.getLogger(__name__)


class AbstractModelService(ABC):
    """Interface satisfied by both the real service and the test fake."""

    @property
    @abstractmethod
    def model_name(self) -> str: ...

    @property
    @abstractmethod
    def vocab_size(self) -> int: ...

    @abstractmethod
    def encode(
        self, text: str, *, add_special_tokens: bool = False
    ) -> tuple[list[int], list[str]]: ...

    @abstractmethod
    def decode(self, token_ids: list[int], *, skip_special_tokens: bool = True) -> str: ...

    @abstractmethod
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
    ) -> tuple[str, str, int, int, int]: ...


class ModelService(AbstractModelService):
    """Wraps a single tokenizer + causal LM instance loaded at startup."""

    def __init__(self, model_name: str | None = None) -> None:
        name = model_name or settings.model_name
        logger.info("Loading tokenizer and model: %s", name)
        tokenizer: PreTrainedTokenizer = AutoTokenizer.from_pretrained(  # type: ignore[assignment]
            name
        )
        # GPT-2 has no pad token; use eos to silence generation warnings.
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        model: PreTrainedModel = AutoModelForCausalLM.from_pretrained(name)
        model.eval()  # type: ignore[no-untyped-call]

        self._model_name = name
        self._tokenizer = tokenizer
        self._model = model
        logger.info("Model loaded: %s (vocab_size=%d)", name, tokenizer.vocab_size)

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def vocab_size(self) -> int:
        return int(self._tokenizer.vocab_size)

    def encode(self, text: str, *, add_special_tokens: bool = False) -> tuple[list[int], list[str]]:
        """Tokenize text; return (token_ids, token_strings)."""
        encoding = self._tokenizer(
            text,
            add_special_tokens=add_special_tokens,
            return_tensors=None,
        )
        ids: list[int] = encoding["input_ids"]
        tokens: list[str] = [cast("str", self._tokenizer.decode([tid])) for tid in ids]
        return ids, tokens

    def decode(self, token_ids: list[int], *, skip_special_tokens: bool = True) -> str:
        """Decode token IDs to text; raises InvalidTokenError on bad ids."""
        bad = [tid for tid in token_ids if not (0 <= tid < self.vocab_size)]
        if bad:
            raise InvalidTokenError(bad, self.vocab_size)
        return cast(
            "str", self._tokenizer.decode(token_ids, skip_special_tokens=skip_special_tokens)
        )

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
        """Generate text from prompt.

        Returns:
            (generated_text, full_text, num_prompt_tokens, num_generated_tokens, latency_ms)
        """
        if seed is not None:
            transformers.set_seed(seed)

        inputs = self._tokenizer(prompt, return_tensors="pt", add_special_tokens=True)
        input_ids: torch.Tensor = inputs["input_ids"]
        num_prompt_tokens = int(input_ids.shape[-1])

        gen_kwargs: dict[str, object] = {
            "max_new_tokens": max_new_tokens,
            "pad_token_id": self._tokenizer.eos_token_id,
        }
        if do_sample:
            gen_kwargs.update(
                {
                    "do_sample": True,
                    "temperature": temperature,
                    "top_k": top_k,
                    "top_p": top_p,
                }
            )
        else:
            gen_kwargs["do_sample"] = False

        t0 = time.perf_counter()
        with torch.no_grad():
            output_ids: torch.Tensor = self._model.generate(input_ids, **gen_kwargs)  # type: ignore[operator]
        latency_ms = int((time.perf_counter() - t0) * 1000)

        new_ids = output_ids[0][num_prompt_tokens:]
        num_generated_tokens = int(new_ids.shape[-1])
        generated_text = cast("str", self._tokenizer.decode(new_ids, skip_special_tokens=True))
        full_text = cast("str", self._tokenizer.decode(output_ids[0], skip_special_tokens=True))

        return generated_text, full_text, num_prompt_tokens, num_generated_tokens, latency_ms
