"""Generic async repository base (Repository Pattern)."""
from typing import Generic, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class AsyncRepository(Generic[ModelT]):
    model: Type[ModelT]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id_: int) -> ModelT | None:
        return await self.session.get(self.model, id_)

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def list_all(self) -> list[ModelT]:
        res = await self.session.execute(select(self.model))
        return list(res.scalars().all())
