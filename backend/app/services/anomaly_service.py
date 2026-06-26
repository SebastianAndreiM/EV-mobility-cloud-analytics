import logging
import os

import joblib
import pandas as pd

from app.core.exceptions import ModelNotTrainedError
from app.core.logging_config import get_logger, log_event
from app.patterns.unit_of_work import UnitOfWork

logger = get_logger("anomaly_service")


class AnomalyDetectionService:
    async def detect(self, limit: int = 500) -> dict:
        async with UnitOfWork() as uow:
            metric = await uow.ml.latest_metric("anomaly")
            if not metric or not os.path.exists(metric.artifact_path):
                raise ModelNotTrainedError("Anomaly model not trained yet")

            sessions = await uow.charging.all_for_training()

        if not sessions:
            return {"model_version": metric.model_version, "scored": 0, "anomalies": []}

        bundle = joblib.load(metric.artifact_path)
        model = bundle["model"]
        features = bundle["features"]

        df = pd.DataFrame([{
            "id": s.id,
            "energy_kwh": s.energy_kwh,
            "duration_minutes": s.duration_minutes,
            "charging_power_kw": s.charging_power_kw,
            "temperature_c": s.temperature_c,
            "average_voltage": s.average_voltage,
            "average_current": s.average_current,
            "vehicle_id": s.vehicle_id,
            "charger_id": s.charger_id,
            "charger_type": s.charger_type,
        } for s in sessions])

        X = df[features].fillna(0)
        # IsolationForest: -1 = anomaly, 1 = normal
        preds = model.predict(X)
        scores = model.decision_function(X)  # lower = more anomalous
        df["is_predicted_anomaly"] = preds == -1
        df["anomaly_score"] = scores

        flagged = df[df["is_predicted_anomaly"]].sort_values("anomaly_score")
        flagged = flagged.head(limit)

        log_event(logger, logging.INFO, "anomaly_detection_run",
                  model_version=metric.model_version,
                  scored=len(df), flagged=int(len(flagged)))

        return {
            "model_version": metric.model_version,
            "scored": int(len(df)),
            "anomalies": [{
                "id": int(r["id"]),
                "vehicle_id": r["vehicle_id"],
                "charger_id": r["charger_id"],
                "charger_type": r["charger_type"],
                "energy_kwh": float(r["energy_kwh"]),
                "duration_minutes": float(r["duration_minutes"]),
                "anomaly_score": round(float(r["anomaly_score"]), 4),
            } for _, r in flagged.iterrows()],
        }