"""Request/response schemas for the generate endpoint."""

from pydantic import BaseModel, Field, field_validator

from app.config import settings


class GenerateRequest(BaseModel):
    """Input for the generate endpoint."""

    prompt: str = Field(..., description="Prompt text to generate from.")
    max_new_tokens: int = Field(50, ge=1, description="Max tokens to generate.")
    temperature: float = Field(1.0, gt=0.0, le=2.0, description="Sampling temperature.")
    top_k: int = Field(50, ge=0, description="Top-k sampling parameter.")
    top_p: float = Field(0.95, gt=0.0, le=1.0, description="Top-p (nucleus) sampling.")
    do_sample: bool = Field(True, description="Use sampling; if False, greedy decoding.")
    seed: int | None = Field(None, ge=0, description="Random seed for reproducibility.")

    @field_validator("prompt")
    @classmethod
    def prompt_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("prompt must not be empty or whitespace-only.")
        if len(v) > 4_000:
            raise ValueError("prompt exceeds maximum length of 4000 characters.")
        return v

    @field_validator("max_new_tokens")
    @classmethod
    def max_tokens_within_limit(cls, v: int) -> int:
        if v > settings.max_new_tokens_limit:
            raise ValueError(
                f"max_new_tokens {v} exceeds server limit of {settings.max_new_tokens_limit}."
            )
        return v


class GenerateParams(BaseModel):
    """Echoed generation parameters in the response."""

    max_new_tokens: int
    temperature: float
    top_k: int
    top_p: float
    do_sample: bool
    seed: int | None


class GenerateResponse(BaseModel):
    """Output from the generate endpoint."""

    prompt: str
    generated_text: str
    full_text: str
    num_prompt_tokens: int
    num_generated_tokens: int
    params: GenerateParams
    model: str
    latency_ms: int
