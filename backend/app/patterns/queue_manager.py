"""Facade Pattern: QueueManager is the single entry point used by services to
enqueue ML jobs and read their status, hiding the broker adapter and Celery
task names behind a small API.
"""
from __future__ import annotations

from app.patterns.broker_adapter import BrokerAdapter

TASK_TRAIN_DURATION = "tasks.train_duration_model"
TASK_TRAIN_ANOMALY = "tasks.train_anomaly_model"


class QueueManager:
    def __init__(self, broker: BrokerAdapter):
        self._broker = broker

    def enqueue_train_duration_model(self, job_id: int) -> str:
        return self._broker.send_task(TASK_TRAIN_DURATION, args=[job_id])

    def enqueue_train_anomaly_model(self, job_id: int) -> str:
        return self._broker.send_task(TASK_TRAIN_ANOMALY, args=[job_id])

    def get_job_status(self, task_id: str) -> str:
        return self._broker.get_status(task_id)
