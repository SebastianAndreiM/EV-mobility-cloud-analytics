"""Unit tests for services in isolation — business logic without HTTP layer.
Proves service/repository separation: we call services directly."""
import pytest

from app.core.exceptions import ConflictError, ModelNotTrainedError, UnauthorizedError
from app.services.analytics_service import AnalyticsService
from app.services.auth_service import AuthService
from app.services.data_generation_service import DataGenerationService
from app.services.job_service import JobService
from app.services.ml_service import MLService


async def test_auth_service_register_then_login(engine):
    auth = AuthService()
    user = await auth.register("svc@test.com", "secret123", "Svc")
    assert user.id is not None
    token = await auth.login("svc@test.com", "secret123")
    assert isinstance(token, str) and len(token) > 10


async def test_auth_service_duplicate_email_raises(engine):
    auth = AuthService()
    await auth.register("dup@test.com", "secret123", None)
    with pytest.raises(ConflictError):
        await auth.register("dup@test.com", "secret123", None)


async def test_auth_service_bad_password_raises(engine):
    auth = AuthService()
    await auth.register("bad@test.com", "secret123", None)
    with pytest.raises(UnauthorizedError):
        await auth.login("bad@test.com", "wrongpass")


async def test_data_generation_service_count(engine):
    svc = DataGenerationService()
    n = await svc.generate(count=25, seed=5)
    assert n == 25


async def test_data_generation_service_delete(engine):
    svc = DataGenerationService()
    await svc.generate(count=10, seed=5)
    deleted = await svc.delete_all()
    assert deleted == 10


async def test_analytics_summary_empty_db_is_zeroed(engine):
    summary = await AnalyticsService().summary()
    assert summary["total_sessions"] == 0
    assert summary["anomaly_rate"] == 0


async def test_analytics_summary_matches_generated(engine):
    await DataGenerationService().generate(count=40, seed=11)
    summary = await AnalyticsService().summary()
    assert summary["total_sessions"] == 40
    assert 0 <= summary["completion_rate"] <= 1
    assert summary["total_energy"] > 0


async def test_analytics_rates_are_consistent(engine):
    await DataGenerationService().generate(count=100, seed=9)
    s = await AnalyticsService().summary()
    perf = await AnalyticsService().charger_performance()
    # every group's session counts should sum to the total
    assert sum(p["sessions"] for p in perf) == s["total_sessions"]


async def test_job_service_creates_queued_job(engine):
    job = await JobService().create_job("train_duration_model")
    assert job.status == "queued"
    fetched = await JobService().get(job.id)
    assert fetched.id == job.id


async def test_ml_service_metrics_without_training_raises(engine):
    with pytest.raises(ModelNotTrainedError):
        await MLService().metrics("duration")
