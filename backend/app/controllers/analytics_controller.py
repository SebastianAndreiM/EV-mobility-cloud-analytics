from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rate_limit import RateLimiter
from app.schemas.analytics_schema import (
    ChargerPerformanceItem, DailyEnergyItem, SummaryResponse,
)
from app.schemas.charging_schema import ChargingSessionResponse
from app.services.analytics_service import AnalyticsService

router = APIRouter(
    prefix="/analytics", tags=["analytics"],
    dependencies=[Depends(RateLimiter(times=60, seconds=60, scope="analytics"))],
)
_service = AnalyticsService()


@router.get("/summary", response_model=SummaryResponse)
async def summary(user=Depends(get_current_user)):
    return await _service.summary()


@router.get("/charger-performance", response_model=list[ChargerPerformanceItem])
async def charger_performance(user=Depends(get_current_user)):
    return await _service.charger_performance()


@router.get("/daily-energy", response_model=list[DailyEnergyItem])
async def daily_energy(user=Depends(get_current_user)):
    return await _service.daily_energy()


@router.get("/anomalies", response_model=list[ChargingSessionResponse])
async def anomalies(user=Depends(get_current_user)):
    return await _service.anomalies()
