import logging

from app.core.logging_config import get_logger, log_event
from app.patterns.data_generator_factory import DataGeneratorFactory
from app.patterns.unit_of_work import UnitOfWork

logger = get_logger("data_generation_service")


class DataGenerationService:
    async def generate(self, count: int, seed: int | None) -> int:
        factory = DataGeneratorFactory.create(seed=seed)
        rows = factory.generate(count)
        async with UnitOfWork() as uow:
            inserted = await uow.charging.bulk_insert(rows)
            await uow.commit()
        log_event(logger, logging.INFO, "data_generated", count=inserted, seed=seed)
        return inserted

    async def delete_all(self) -> int:
        async with UnitOfWork() as uow:
            deleted = await uow.charging.delete_all()
            await uow.commit()
        log_event(logger, logging.INFO, "data_deleted", count=deleted)
        return deleted
