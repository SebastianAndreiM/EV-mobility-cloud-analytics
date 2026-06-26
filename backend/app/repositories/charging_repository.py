from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.charging_session import ChargingSession
from app.patterns.repository import AsyncRepository


class ChargingRepository(AsyncRepository[ChargingSession]):
    model = ChargingSession

    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def bulk_insert(self, rows: list[dict]) -> int:
        objs = [ChargingSession(**r) for r in rows]
        self.session.add_all(objs)
        await self.session.flush()
        return len(objs)

    def _apply_filters(self, stmt, charger_type, status, min_temp, max_temp, anomaly_only):
        if charger_type:
            stmt = stmt.where(ChargingSession.charger_type == charger_type)
        if status:
            stmt = stmt.where(ChargingSession.status == status)
        if min_temp is not None:
            stmt = stmt.where(ChargingSession.temperature_c >= min_temp)
        if max_temp is not None:
            stmt = stmt.where(ChargingSession.temperature_c <= max_temp)
        if anomaly_only:
            stmt = stmt.where(ChargingSession.is_anomaly.is_(True))
        return stmt

    async def paginate(self, page, page_size, charger_type=None, status=None,
                       min_temp=None, max_temp=None, anomaly_only=False):
        base = select(ChargingSession)
        base = self._apply_filters(base, charger_type, status, min_temp, max_temp, anomaly_only)
        count_stmt = select(func.count()).select_from(base.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()
        stmt = base.order_by(ChargingSession.id.desc()).offset((page - 1) * page_size).limit(page_size)
        items = list((await self.session.execute(stmt)).scalars().all())
        return total, items

    async def delete_all(self) -> int:
        res = await self.session.execute(delete(ChargingSession))
        return res.rowcount or 0

    async def count(self) -> int:
        return (await self.session.execute(select(func.count(ChargingSession.id)))).scalar_one()

    async def all_for_training(self) -> list[ChargingSession]:
        res = await self.session.execute(select(ChargingSession))
        return list(res.scalars().all())

    async def anomalies(self) -> list[ChargingSession]:
        res = await self.session.execute(
            select(ChargingSession).where(ChargingSession.is_anomaly.is_(True))
        )
        return list(res.scalars().all())
