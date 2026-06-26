from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job
from app.patterns.repository import AsyncRepository


class JobRepository(AsyncRepository[Job]):
    model = Job

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def list_recent(self, limit: int = 50) -> list[Job]:
        res = await self.session.execute(
            select(Job).order_by(Job.id.desc()).limit(limit)
        )
        return list(res.scalars().all())
