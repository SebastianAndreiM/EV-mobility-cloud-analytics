from datetime import datetime

from pydantic import BaseModel, Field


class TrainResponse(BaseModel):
    job_id: int
    status: str


class MetricsResponse(BaseModel):
    model_type: str
    model_version: str
    mae: float | None = None
    rmse: float | None = None
    r2: float | None = None
    training_rows: int
    trained_at: datetime

    model_config = {"from_attributes": True}


class PredictDurationRequest(BaseModel):
    charger_type: str = Field(pattern="^(slow|fast|ultra_fast)$")
    start_battery_percent: float = Field(ge=0, le=100)
    end_battery_percent: float = Field(ge=0, le=100)
    battery_capacity_kwh: float = Field(gt=0)
    charging_power_kw: float = Field(gt=0)
    temperature_c: float
    average_voltage: float = Field(gt=0)
    average_current: float = Field(gt=0)


class PredictDurationResponse(BaseModel):
    predicted_duration_minutes: float
    model_version: str
    confidence_note: str

class DetectedAnomaly(BaseModel):
    id: int
    vehicle_id: str
    charger_id: str
    charger_type: str
    energy_kwh: float
    duration_minutes: float
    anomaly_score: float


class AnomalyDetectionResponse(BaseModel):
    model_version: str
    scored: int
    anomalies: list[DetectedAnomaly]