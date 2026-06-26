"""Celery tasks. Synchronous DB access (Celery is not async-friendly).

Task names are explicit and MUST match the constants in
app/patterns/queue_manager.py:
    tasks.train_duration_model
    tasks.train_anomaly_model
"""
import logging
from datetime import datetime, timezone

import pandas as pd

from app.core.config import settings
from app.core.logging_config import configure_logging, get_logger, log_event
from app.db.session import get_sync_session
from app.models.charging_session import ChargingSession
from app.models.job import Job
from app.models.ml_model import MLModelMetric
from app.patterns.model_strategy import (
    IsolationForestAnomalyStrategy, RandomForestDurationStrategy,
)
from app.workers.celery_app import celery_app

configure_logging()
logger = get_logger("celery_tasks")


def _set_status(session, job_id: int, status: str, detail: str | None = None) -> None:
    job = session.get(Job, job_id)
    if job:
        job.status = status
        if detail:
            job.detail = detail
        job.updated_at = datetime.now(timezone.utc)
        session.flush()
    log_event(logger, logging.INFO, "job_status_changed", job_id=job_id, status=status)


def _load_dataframe(session) -> pd.DataFrame:
    rows = session.query(ChargingSession).all()
    records = [{
        "charger_type": r.charger_type,
        "start_battery_percent": r.start_battery_percent,
        "end_battery_percent": r.end_battery_percent,
        "battery_capacity_kwh": r.battery_capacity_kwh,
        "charging_power_kw": r.charging_power_kw,
        "temperature_c": r.temperature_c,
        "average_voltage": r.average_voltage,
        "average_current": r.average_current,
        "energy_kwh": r.energy_kwh,
        "duration_minutes": r.duration_minutes,
    } for r in rows]
    return pd.DataFrame(records)


def _train(strategy, job_id: int):
    with get_sync_session() as session:
        try:
            _set_status(session, job_id, "running")
            df = _load_dataframe(session)
            if len(df) < 20:
                _set_status(session, job_id, "failed", "Not enough data (need >= 20 rows)")
                return {"status": "failed", "reason": "insufficient_data"}
            result = strategy.train(df, artifacts_dir=settings.MODEL_ARTIFACTS_DIR)
            metric = MLModelMetric(
                model_type=result["model_type"],
                model_version=result["model_version"],
                artifact_path=result["artifact_path"],
                mae=result["mae"], rmse=result["rmse"], r2=result["r2"],
                training_rows=result["training_rows"],
            )
            session.add(metric)
            _set_status(session, job_id, "completed", f"version={result['model_version']}")
            return {"status": "completed", "version": result["model_version"]}
        except Exception as exc:  # noqa: BLE001
            _set_status(session, job_id, "failed", str(exc))
            log_event(logger, logging.ERROR, "training_failed", job_id=job_id)
            raise


@celery_app.task(name="tasks.train_duration_model")
def train_duration_model(job_id: int):
    return _train(RandomForestDurationStrategy(), job_id)


@celery_app.task(name="tasks.train_anomaly_model")
def train_anomaly_model(job_id: int):
    return _train(IsolationForestAnomalyStrategy(), job_id)
