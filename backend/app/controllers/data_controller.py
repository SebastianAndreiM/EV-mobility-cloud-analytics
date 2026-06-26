from fastapi import APIRouter, Depends, Query

from app.core.deps import get_current_user
from app.core.exceptions import NotFoundError
from app.schemas.charging_schema import (
    ChargingSessionResponse, GenerateRequest, GenerateResponse, PaginatedSessions,
)
from app.patterns.unit_of_work import UnitOfWork
from app.services.data_generation_service import DataGenerationService

router = APIRouter(prefix="/data", tags=["data"])
_service = DataGenerationService()


@router.post("/generate", response_model=GenerateResponse)
async def generate(body: GenerateRequest, user=Depends(get_current_user)):
    n = await _service.generate(body.count, body.seed)
    return GenerateResponse(generated=n, seed=body.seed)


@router.get("/sessions", response_model=PaginatedSessions)
async def list_sessions(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=200),
    charger_type: str | None = None,
    status: str | None = None,
    min_temperature: float | None = None,
    max_temperature: float | None = None,
    anomaly_only: bool = False,
    user=Depends(get_current_user),
):
    async with UnitOfWork() as uow:
        total, items = await uow.charging.paginate(
            page, page_size, charger_type, status,
            min_temperature, max_temperature, anomaly_only,
        )
    return PaginatedSessions(total=total, page=page, page_size=page_size, items=items)


@router.get("/sessions/{session_id}", response_model=ChargingSessionResponse)
async def get_session(session_id: int, user=Depends(get_current_user)):
    async with UnitOfWork() as uow:
        s = await uow.charging.get(session_id)
        if not s:
            raise NotFoundError("Session not found")
        return s


@router.delete("/sessions")
async def delete_sessions(user=Depends(get_current_user)):
    deleted = await _service.delete_all()
    return {"deleted": deleted}
