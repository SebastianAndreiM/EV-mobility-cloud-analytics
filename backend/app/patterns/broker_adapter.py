"""Adapter Pattern: wraps Celery so the rest of the app does not import Celery
internals directly. Makes the broker swappable/manageable and easy to mock.

Uses the registered task's apply_async (not Celery.send_task) so that
task_always_eager works in tests, while behaving identically in production.
"""
from __future__ import annotations

from typing import Any


class BrokerAdapter:
    def __init__(self, celery_app):
        self._celery = celery_app

    def send_task(self, name: str, args: list[Any] | None = None) -> str:
        task = self._celery.tasks[name]
        result = task.apply_async(args=args or [])
        return result.id

    def get_status(self, task_id: str) -> str:
        return self._celery.AsyncResult(task_id).status
