"""Application configuration loaded from environment variables.

A single DATABASE_URL is provided by the environment. FastAPI needs the
asyncpg driver while the Celery worker needs a sync psycopg2 driver, so we
derive both URLs from the same base to avoid drift between services.
"""
from functools import lru_cache
from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- App ---
    APP_NAME: str = "EV Mobility Cloud Analytics"
    ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = ""

    # --- Security ---
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- Database ---
    # Canonical URL. May be given with or without an explicit driver.
    # e.g. postgresql://user:pass@db:5432/evdb
    DATABASE_URL: str = "postgresql://ev_user:ev_pass@db:5432/ev_analytics"

    # --- Redis ---
    # /0 rate-limit, /1 celery results, /2 cache  (separate indices, no collisions)
    REDIS_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/1"
    CACHE_REDIS_URL: str = "redis://redis:6379/2"

    # --- RabbitMQ / Celery broker ---
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # --- ML ---
    MODEL_ARTIFACTS_DIR: str = "app/artifacts/models"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, v):
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def async_database_url(self) -> str:
        """URL forced onto the asyncpg driver for FastAPI."""
        return self._with_driver("postgresql+asyncpg")

    @property
    def sync_database_url(self) -> str:
        """URL forced onto the psycopg2 driver for Celery / Alembic."""
        return self._with_driver("postgresql+psycopg2")

    def _with_driver(self, driver: str) -> str:
        url = self.DATABASE_URL
        # strip any existing +driver portion in the scheme
        if "://" in url:
            scheme, rest = url.split("://", 1)
            base_scheme = scheme.split("+", 1)[0]  # postgresql
            return f"{driver}://{rest}" if base_scheme else url
        return url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
