from datetime import datetime

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    count: int = Field(default=1000, ge=1, le=200000)
    seed: int | None = None


class GenerateResponse(BaseModel):
    generated: int
    seed: int | None


class ChargingSessionResponse(BaseModel):
    id: int
    vehicle_id: str
    charger_id: str
    charger_type: str
    connector_type: str
    location: str
    start_time: datetime
    end_time: datetime
    start_battery_percent: float
    end_battery_percent: float
    battery_capacity_kwh: float
    energy_kwh: float
    charging_power_kw: float
    average_voltage: float
    average_current: float
    temperature_c: float
    duration_minutes: float
    cost_eur: float
    status: str
    is_anomaly: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedSessions(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[ChargingSessionResponse]
