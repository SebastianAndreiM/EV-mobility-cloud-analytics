"""Unit tests for config driver derivation — the source of the async/sync
consistency guarantee. No DB, no I/O."""
from app.core.config import Settings


def test_async_url_uses_asyncpg():
    s = Settings(DATABASE_URL="postgresql://u:p@db:5432/x")
    assert s.async_database_url == "postgresql+asyncpg://u:p@db:5432/x"


def test_sync_url_uses_psycopg2():
    s = Settings(DATABASE_URL="postgresql://u:p@db:5432/x")
    assert s.sync_database_url == "postgresql+psycopg2://u:p@db:5432/x"


def test_existing_driver_is_overridden_not_duplicated():
    s = Settings(DATABASE_URL="postgresql+psycopg2://u:p@db:5432/x")
    assert s.async_database_url == "postgresql+asyncpg://u:p@db:5432/x"
    assert "psycopg2" not in s.async_database_url


def test_cors_origins_parsed_from_csv_string():
    s = Settings(CORS_ORIGINS="http://a.com, http://b.com")
    assert s.CORS_ORIGINS == ["http://a.com", "http://b.com"]
