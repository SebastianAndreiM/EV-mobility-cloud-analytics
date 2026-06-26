from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.core.rate_limit import RateLimiter
from app.schemas.ml_schema import (
    AnomalyDetectionResponse, MetricsResponse, PredictDurationRequest,
    PredictDurationResponse, TrainResponse,
)
from app.services.anomaly_service import AnomalyDetectionService
from app.services.ml_service import MLService
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="/ml", tags=["ml"])
@router.post("/train-duration-model", response_model=TrainResponse)
async def train_duration(user=Depends(get_current_user)):
    return await MLService().train_duration()


@router.post("/train-anomaly-model", response_model=TrainResponse)
async def train_anomaly(user=Depends(get_current_user)):
    return await MLService().train_anomaly()


@router.get("/metrics", response_model=MetricsResponse)
async def metrics(model_type: str = "duration", user=Depends(get_current_user)):
    return await MLService().metrics(model_type)

@router.post("/detect-anomalies", response_model=AnomalyDetectionResponse)
async def detect_anomalies(limit: int = 100, user=Depends(get_current_user)):
    return await AnomalyDetectionService().detect(limit=limit)

@router.post(
    "/predict-duration", response_model=PredictDurationResponse,
    dependencies=[Depends(RateLimiter(times=30, seconds=60, scope="predict"))],
)
async def predict_duration(body: PredictDurationRequest, user=Depends(get_current_user)):
    return await PredictionService().predict_duration(body.model_dump(), user.id)
