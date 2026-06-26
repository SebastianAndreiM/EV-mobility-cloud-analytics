"""Session/engine factories.

- Async engine + AsyncSession: used by FastAPI request handlers.
- Sync engine + Session: used by Celery tasks (Celery is not async-friendly).

Both read the same canonical DATABASE_URL via settings and only differ by
driver, so there is one source of truth for the database location.
"""
from collections.abc import AsyncGenerator
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# --- Async (FastAPI) ---
async_engine = create_async_engine(
    settings.async_database_url, echo=False, pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# --- Sync (Celery worker) ---
sync_engine = create_engine(
    settings.sync_database_url, echo=False, pool_pre_ping=True
)
SyncSessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)


@contextmanager
def get_sync_session() -> Iterator[Session]:
    session = SyncSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


async def init_models() -> None:
    """Create tables on startup (dev convenience; prefer Alembic in prod)."""
    from app.db.database import Base  # noqa: F401
    import app.models  # noqa: F401  ensure models are imported/registered

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
