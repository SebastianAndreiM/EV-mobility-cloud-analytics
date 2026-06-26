import logging
import os

import joblib

from app.core.exceptions import ModelNotTrainedError
from app.core.logging_config import get_logger, log_event
from app.models.prediction_log import PredictionLog
from app.patterns.model_strategy import RandomForestDurationStrategy
from app.patterns.unit_of_work import UnitOfWork

logger = get_logger("prediction_service")


class PredictionService:
    def __init__(self):
        self.strategy = RandomForestDurationStrategy()

    async def predict_duration(self, payload: dict, user_id: int | None) -> dict:
        async with UnitOfWork() as uow:
            metric = await uow.ml.latest_metric("duration")
            if not metric or not os.path.exists(metric.artifact_path):
                raise ModelNotTrainedError("Duration model not trained yet")
            model = joblib.load(metric.artifact_path)
            predicted = self.strategy.predict(model, payload)
            predicted = max(round(predicted, 1), 0.1)

            log = PredictionLog(
                user_id=user_id,
                model_version=metric.model_version,
                input_payload=payload,
                predicted_duration_minutes=predicted,
            )
            await uow.ml.add_prediction_log(log)
            await uow.commit()

        log_event(logger, logging.INFO, "prediction_made",
                  user_id=user_id, model_version=metric.model_version,
                  predicted_duration_minutes=predicted)
        return {
            "predicted_duration_minutes": predicted,
            "model_version": metric.model_version,
            "confidence_note": f"RandomForest, R2={metric.r2:.3f}" if metric.r2 is not None
            else "RandomForest model",
        }
