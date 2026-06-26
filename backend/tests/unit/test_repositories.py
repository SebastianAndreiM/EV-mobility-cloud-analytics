"""Unit tests for repositories in isolation — direct DB access, no HTTP, no
services. Proves the repository layer is independently testable."""
import pytest

from app.models.user import User
from app.patterns.data_generator_factory import DataGeneratorFactory
from app.repositories.charging_repository import ChargingRepository
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository
from app.models.job import Job


async def test_user_repo_add_and_get_by_email(db_session):
    repo = UserRepository(db_session)
    await repo.add(User(email="x@y.com", hashed_password="h"))
    await db_session.commit()
    found = await repo.get_by_email("x@y.com")
    assert found is not None and found.email == "x@y.com"


async def test_user_repo_missing_email_returns_none(db_session):
    repo = UserRepository(db_session)
    assert await repo.get_by_email("nobody@y.com") is None


async def test_charging_repo_bulk_insert_and_count(db_session):
    repo = ChargingRepository(db_session)
    rows = DataGeneratorFactory.create(seed=1).generate(30)
    inserted = await repo.bulk_insert(rows)
    await db_session.commit()
    assert inserted == 30
    assert await repo.count() == 30


async def test_charging_repo_filter_anomaly_only(db_session):
    repo = ChargingRepository(db_session)
    rows = DataGeneratorFactory.create(seed=7).generate(200)
    await repo.bulk_insert(rows)
    await db_session.commit()
    total, items = await repo.paginate(page=1, page_size=500, anomaly_only=True)
    assert all(s.is_anomaly for s in items)
    assert total == len(items)


async def test_charging_repo_filter_by_charger_type(db_session):
    repo = ChargingRepository(db_session)
    await repo.bulk_insert(DataGeneratorFactory.create(seed=3).generate(150))
    await db_session.commit()
    _, items = await repo.paginate(page=1, page_size=500, charger_type="slow")
    assert all(s.charger_type == "slow" for s in items)


async def test_charging_repo_pagination_bounds(db_session):
    repo = ChargingRepository(db_session)
    await repo.bulk_insert(DataGeneratorFactory.create(seed=2).generate(45))
    await db_session.commit()
    total, items = await repo.paginate(page=2, page_size=20)
    assert total == 45
    assert len(items) == 20  # second page of 45 -> 20


async def test_charging_repo_delete_all(db_session):
    repo = ChargingRepository(db_session)
    await repo.bulk_insert(DataGeneratorFactory.create(seed=2).generate(10))
    await db_session.commit()
    deleted = await repo.delete_all()
    await db_session.commit()
    assert deleted == 10
    assert await repo.count() == 0


async def test_job_repo_list_recent_orders_desc(db_session):
    repo = JobRepository(db_session)
    for t in ["a", "b", "c"]:
        await repo.add(Job(job_type=t, status="queued"))
    await db_session.commit()
    recent = await repo.list_recent()
    assert [j.job_type for j in recent[:3]] == ["c", "b", "a"]
