import logging

from app.core.exceptions import ModelNotTrainedError
from app.core.logging_config import get_logger, log_event
from app.patterns.queue_manager import QueueManager
from app.patterns.broker_adapter import BrokerAdapter
from app.patterns.unit_of_work import UnitOfWork
from app.services.job_service import JobService

logger = get_logger("ml_service")


class MLService:
    def __init__(self):
        # Import here to avoid importing Celery at module import time in tests.
        from app.workers.celery_app import celery_app
        self.queue = QueueManager(BrokerAdapter(celery_app))
        self.jobs = JobService()

    async def train_duration(self) -> dict:
        job = await self.jobs.create_job("train_duration_model")
        task_id = self.queue.enqueue_train_duration_model(job.id)
        await self.jobs.set_celery_task_id(job.id, task_id)
        log_event(logger, logging.INFO, "train_enqueued", job_id=job.id, model="duration")
        return {"job_id": job.id, "status": "queued"}

    async def train_anomaly(self) -> dict:
        job = await self.jobs.create_job("train_anomaly_model")
        task_id = self.queue.enqueue_train_anomaly_model(job.id)
        await self.jobs.set_celery_task_id(job.id, task_id)
        log_event(logger, logging.INFO, "train_enqueued", job_id=job.id, model="anomaly")
        return {"job_id": job.id, "status": "queued"}

    async def metrics(self, model_type: str = "duration"):
        async with UnitOfWork() as uow:
            metric = await uow.ml.latest_metric(model_type)
            if not metric:
                raise ModelNotTrainedError(f"No {model_type} model trained yet")
            return metric
