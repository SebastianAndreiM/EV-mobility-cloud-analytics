from app.models.job import Job
from app.patterns.unit_of_work import UnitOfWork


class JobService:
    async def create_job(self, job_type: str) -> Job:
        async with UnitOfWork() as uow:
            job = Job(job_type=job_type, status="queued")
            await uow.jobs.add(job)
            await uow.commit()
            await uow._session.refresh(job)
            return job

    async def set_celery_task_id(self, job_id: int, task_id: str) -> None:
        async with UnitOfWork() as uow:
            job = await uow.jobs.get(job_id)
            if job:
                job.celery_task_id = task_id
                await uow.commit()

    async def get(self, job_id: int) -> Job | None:
        async with UnitOfWork() as uow:
            return await uow.jobs.get(job_id)

    async def list_recent(self) -> list[Job]:
        async with UnitOfWork() as uow:
            return await uow.jobs.list_recent()
