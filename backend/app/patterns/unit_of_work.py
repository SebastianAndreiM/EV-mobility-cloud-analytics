"""Unit of Work (transaction boundary) for async sessions."""
from app.db.session import AsyncSessionLocal
from app.repositories.user_repository import UserRepository
from app.repositories.charging_repository import ChargingRepository
from app.repositories.ml_repository import MLRepository
from app.repositories.job_repository import JobRepository


class UnitOfWork:
    def __init__(self):
        self._session = None

    async def __aenter__(self):
        self._session = AsyncSessionLocal()
        self.users = UserRepository(self._session)
        self.charging = ChargingRepository(self._session)
        self.ml = MLRepository(self._session)
        self.jobs = JobRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self._session.rollback()
        await self._session.close()

    async def commit(self):
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
