"""Import all models so they register on Base.metadata."""
from app.models.user import Account, AuthCredential
from app.models.charging_session import ChargingSession
from app.models.ml_model import MLModelMetric
from app.models.prediction_log import PredictionLog
from app.models.job import Job

__all__ = [
    "Account", "AuthCredential", "ChargingSession",
    "MLModelMetric", "PredictionLog", "Job",
]