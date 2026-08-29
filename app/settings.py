"""Application settings and configuration loading."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ai_provider: str = Field(default="mock", alias="AI_PROVIDER")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    anthropic_api_key: str | None = Field(default=None, alias="ANTHROPIC_API_KEY")
    anthropic_model: str = Field(default="claude-3-5-haiku-latest", alias="ANTHROPIC_MODEL")
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    telemetry_db_path: str = Field(default="data/telemetry.db", alias="TELEMETRY_DB_PATH")
    config_dir: str = Field(default="config", alias="CONFIG_DIR")
    host: str = Field(default="0.0.0.0", alias="HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    default_manual_minutes: int = Field(default=75, alias="DEFAULT_MANUAL_MINUTES")

    @property
    def config_path(self) -> Path:
        path = Path(self.config_dir)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path

    @property
    def db_path(self) -> Path:
        path = Path(self.telemetry_db_path)
        if not path.is_absolute():
            path = ROOT_DIR / path
        return path


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()


def load_yaml(name: str) -> dict[str, Any]:
    """Load a YAML configuration file from the config directory."""
    settings = get_settings()
    path = settings.config_path / name
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config {name} must be a mapping")
    return data


def ensure_data_dir() -> None:
    """Ensure telemetry data directory exists."""
    get_settings().db_path.parent.mkdir(parents=True, exist_ok=True)


def provider_name() -> str:
    """Resolve active AI provider, falling back to mock when credentials missing."""
    settings = get_settings()
    requested = settings.ai_provider.lower().strip() or "mock"
    if requested == "openai" and not settings.openai_api_key:
        return "mock"
    if requested == "anthropic" and not settings.anthropic_api_key:
        return "mock"
    if requested not in {"mock", "openai", "anthropic"}:
        return "mock"
    return requested


def env_or_default(key: str, default: str) -> str:
    """Read an environment variable with a default."""
    return os.environ.get(key, default)
