from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ml_model import MLModelMetric
from app.models.prediction_log import PredictionLog
from app.patterns.repository import AsyncRepository


class MLRepository(AsyncRepository[MLModelMetric]):
    model = MLModelMetric

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def latest_metric(self, model_type: str) -> MLModelMetric | None:
        res = await self.session.execute(
            select(MLModelMetric)
            .where(MLModelMetric.model_type == model_type)
            .order_by(MLModelMetric.trained_at.desc())
            .limit(1)
        )
        return res.scalar_one_or_none()

    async def add_prediction_log(self, log: PredictionLog) -> PredictionLog:
        self.session.add(log)
        await self.session.flush()
        return log
