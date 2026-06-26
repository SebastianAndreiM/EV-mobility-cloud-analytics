from pydantic import BaseModel


class SummaryResponse(BaseModel):
    total_sessions: int
    average_duration: float
    average_energy: float
    average_power: float
    anomaly_rate: float
    completion_rate: float
    total_energy: float
    total_cost: float


class ChargerPerformanceItem(BaseModel):
    charger_type: str
    charger_id: str
    sessions: int
    avg_energy: float
    avg_duration: float
    avg_power: float


class DailyEnergyItem(BaseModel):
    day: str
    total_energy: float
    sessions: int
