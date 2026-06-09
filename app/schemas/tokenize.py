"""Request/response schemas for encode and decode endpoints."""

from pydantic import BaseModel, Field, field_validator

from app.config import settings


class EncodeRequest(BaseModel):
    """Input for the encode endpoint."""

    text: str = Field(..., description="Text to tokenize.")
    add_special_tokens: bool = Field(False, description="Whether to add special tokens.")

    @field_validator("text")
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        stripped = v.strip()
        if not stripped:
            raise ValueError("text must not be empty or whitespace-only.")
        if len(v) > settings.max_input_chars:
            raise ValueError(f"text exceeds max length of {settings.max_input_chars} characters.")
        return v


class EncodeResponse(BaseModel):
    """Output from the encode endpoint."""

    input_text: str
    token_ids: list[int]
    tokens: list[str]
    num_tokens: int
    model: str


class DecodeRequest(BaseModel):
    """Input for the decode endpoint."""

    token_ids: list[int] = Field(..., description="Token IDs to decode.")
    skip_special_tokens: bool = Field(True, description="Whether to skip special tokens.")

    @field_validator("token_ids")
    @classmethod
    def ids_not_empty(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("token_ids must not be empty.")
        if len(v) > settings.max_token_ids:
            raise ValueError(f"token_ids length exceeds maximum of {settings.max_token_ids}.")
        return v


class DecodeResponse(BaseModel):
    """Output from the decode endpoint."""

    token_ids: list[int]
    text: str
    model: str
