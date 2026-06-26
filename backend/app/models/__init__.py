"""Import all models so they register on Base.metadata."""
from app.models.user import User
from app.models.charging_session import ChargingSession
from app.models.ml_model import MLModelMetric
from app.models.prediction_log import PredictionLog
from app.models.job import Job

__all__ = ["User", "ChargingSession", "MLModelMetric", "PredictionLog", "Job"]
