"""Backend configuration loaded from environment variables."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Validated application settings."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "staging", "production"] = Field(
        default="development",
        description="Deployment environment for the backend.",
    )
    supabase_url: str = Field(description="Supabase project URL.")
    supabase_anon_key: SecretStr = Field(description="Supabase anonymous key.")
    supabase_service_role_key: SecretStr = Field(
        description="Supabase service-role key.",
    )
    database_url: SecretStr = Field(
        description="PostgreSQL connection URL for migrations and database access.",
    )
    openai_api_key: SecretStr = Field(description="OpenAI-compatible provider API key.")
    openai_embedding_model: str = Field(
        description="Embedding model used for document retrieval.",
    )
    openai_embedding_dimensions: Annotated[int, Field(gt=0)] = Field(
        description="Embedding vector dimensions.",
    )
    allowed_origins: Annotated[list[str], NoDecode] = Field(
        description="Browser origins allowed to call the API.",
    )

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, value: str | list[str]) -> list[str]:
        """Parse comma-separated origins from the environment."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
