"""Celery application. Broker = RabbitMQ, result backend = Redis."""
from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "ev_mobility",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    timezone="UTC",
    # eager mode is toggled on in tests via CELERY_TASK_ALWAYS_EAGER
)

# Ensure tasks are registered when the worker starts (-A app.workers.celery_app)
import app.workers.tasks  # noqa: E402,F401
