from datetime import datetime

from pydantic import BaseModel


class JobResponse(BaseModel):
    id: int
    celery_task_id: str | None = None
    job_type: str
    status: str
    detail: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
