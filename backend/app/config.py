"""
Application configuration using Pydantic Settings.

All configuration values are loaded from environment variables or a `.env` file.
Nested models provide logical grouping for database, auth, OpenAI, and CORS settings.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Root application settings populated from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "InsightFlow"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "development"
    log_level: str = "INFO"

    # ── Server ───────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000

    # ── Database ─────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./insightflow.db"

    # ── Redis ────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379/0"

    # ── Security / JWT ───────────────────────────────────────────
    secret_key: str = "change-me-to-a-random-64-char-hex-string"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # ── CORS ─────────────────────────────────────────────────────
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Accept a JSON-encoded string or a Python list."""
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except (json.JSONDecodeError, TypeError):
                return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v  # type: ignore[return-value]

    # ── OpenAI ───────────────────────────────────────────────────
    openai_api_key: str = ""
    openai_base_url: str = ""  # Base URL for custom endpoints like Groq
    openai_model: str = "gpt-4o"
    openai_max_tokens: int = 4096

    # ── File Upload ──────────────────────────────────────────────
    max_upload_size_mb: int = 100
    upload_dir: str = "./uploads"

    # ── User Data Schema ─────────────────────────────────────────
    user_data_schema: str = "user_data"

    # ── Derived Properties ───────────────────────────────────────
    @property
    def max_upload_size_bytes(self) -> int:
        """Maximum upload size expressed in bytes."""
        return self.max_upload_size_mb * 1024 * 1024

    @property
    def upload_path(self) -> Path:
        """Resolved upload directory as a ``Path``."""
        path = Path(self.upload_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()
