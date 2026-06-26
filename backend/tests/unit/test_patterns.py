"""Unit tests for Adapter + Facade patterns using a fake Celery, so no broker
is required. Verifies QueueManager delegates to the right task names."""
from app.patterns.broker_adapter import BrokerAdapter
from app.patterns.queue_manager import (
    QueueManager, TASK_TRAIN_DURATION, TASK_TRAIN_ANOMALY,
)


class _FakeResult:
    def __init__(self, id_):
        self.id = id_
        self.status = "PENDING"


class _FakeTask:
    def __init__(self, name, calls):
        self.name = name
        self._calls = calls

    def apply_async(self, args=None):
        self._calls.append((self.name, args))
        return _FakeResult(f"task-{len(self._calls)}")


class _FakeCelery:
    def __init__(self):
        self.calls = []
        self.tasks = {
            TASK_TRAIN_DURATION: _FakeTask(TASK_TRAIN_DURATION, self.calls),
            TASK_TRAIN_ANOMALY: _FakeTask(TASK_TRAIN_ANOMALY, self.calls),
        }

    def AsyncResult(self, task_id):
        r = _FakeResult(task_id)
        r.status = "SUCCESS"
        return r


def test_queue_manager_enqueues_duration_task():
    fake = _FakeCelery()
    qm = QueueManager(BrokerAdapter(fake))
    task_id = qm.enqueue_train_duration_model(job_id=7)
    assert fake.calls[0] == (TASK_TRAIN_DURATION, [7])
    assert task_id.startswith("task-")


def test_queue_manager_enqueues_anomaly_task():
    fake = _FakeCelery()
    qm = QueueManager(BrokerAdapter(fake))
    qm.enqueue_train_anomaly_model(job_id=9)
    assert fake.calls[0] == (TASK_TRAIN_ANOMALY, [9])


def test_queue_manager_reads_status():
    fake = _FakeCelery()
    qm = QueueManager(BrokerAdapter(fake))
    assert qm.get_job_status("abc") == "SUCCESS"


def test_broker_adapter_uses_registered_task():
    """Guards the eager-mode bug: adapter must use the task object, not
    Celery.send_task."""
    fake = _FakeCelery()
    adapter = BrokerAdapter(fake)
    adapter.send_task(TASK_TRAIN_DURATION, args=[1])
    assert fake.calls[0][0] == TASK_TRAIN_DURATION
