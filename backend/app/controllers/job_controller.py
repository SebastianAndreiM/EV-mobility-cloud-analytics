from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.schemas.job_schema import JobResponse
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["jobs"])
_service = JobService()


@router.get("", response_model=list[JobResponse])
async def list_jobs(user=Depends(get_current_user)):
    return await _service.list_recent()


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: int, user=Depends(get_current_user)):
    job = await _service.get(job_id)
    if not job:
        raise NotFoundError("Job not found")
    return job
