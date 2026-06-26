"""Test fixtures: shared SQLite DB (async + sync), eager Celery, fake Redis.

Key correctness points discovered during the compile pass:
- Celery `send_task`/result access touches the result backend even in eager
  mode, so we swap the backend to an in-memory cache backend for tests.
- The Celery task uses the SYNC session while the API uses the ASYNC session.
  In production both point at the same Postgres. In tests we point BOTH at the
  same on-disk SQLite file so the eager task sees the data the API generated.
"""
import os

import pytest
import pytest_asyncio

os.environ.setdefault("JWT_SECRET", "test-secret")

DB_FILE = "./test_shared.db"
if os.path.exists(DB_FILE):
    os.remove(DB_FILE)
os.environ["DATABASE_URL"] = f"sqlite:///{DB_FILE}"  # base; drivers derived per engine

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

import app.db.session as session_module
import app.patterns.unit_of_work as uow_mod
from app.db.database import Base
import app.models  # noqa: F401


@pytest_asyncio.fixture(scope="function")
async def engine():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    async_eng = create_async_engine(f"sqlite+aiosqlite:///{DB_FILE}")
    sync_eng = create_engine(f"sqlite:///{DB_FILE}")

    session_module.async_engine = async_eng
    session_module.AsyncSessionLocal = async_sessionmaker(async_eng, expire_on_commit=False)
    session_module.sync_engine = sync_eng
    session_module.SyncSessionLocal = sessionmaker(bind=sync_eng, autoflush=False, autocommit=False)
    uow_mod.AsyncSessionLocal = session_module.AsyncSessionLocal

    async with async_eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield async_eng
    await async_eng.dispose()
    sync_eng.dispose()


@pytest.fixture(autouse=True)
def eager_celery():
    from app.workers.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    celery_app.conf.task_store_eager_result = True
    celery_app.conf.result_backend = "cache+memory://"
    yield


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    import fakeredis.aioredis as fakeaioredis
    import app.core.rate_limit as rl
    fake = fakeaioredis.FakeRedis(decode_responses=True)

    async def _get_redis():
        return fake

    rl._redis = fake
    monkeypatch.setattr(rl, "get_redis", _get_redis)
    yield


@pytest_asyncio.fixture
async def db_session(engine):
    """Raw AsyncSession for unit-testing repositories/services without HTTP."""
    async with session_module.AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(engine):
    from httpx import ASGITransport, AsyncClient
    from app.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
