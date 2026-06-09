"""Application configuration via environment variables."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All runtime configuration, resolved from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Model
    model_name: str = "gpt2"
    hf_home: str = "/models"

    # Input limits
    max_input_chars: int = 10_000
    max_token_ids: int = 4_096
    max_new_tokens_limit: int = 512

    # Database
    database_url: str = ""
    enable_history: bool = True

    # API
    log_level: str = "INFO"
    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]


settings = Settings()
