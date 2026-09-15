"""Application configuration."""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ai_provider: str = "mock"
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    database_path: str = "data/telemetry.duckdb"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    log_level: str = "INFO"
    app_name: str = "Enterprise AI Engineering Blueprint"
    app_version: str = "0.1.0"
    build_sha: str = "local-dev"
    require_approval_for: str = "HIGH"
    block_critical: bool = True

    @property
    def db_path(self) -> Path:
        return Path(self.database_path)


@lru_cache
def get_settings() -> Settings:
    return Settings()
