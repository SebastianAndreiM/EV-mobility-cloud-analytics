"""Strategy Pattern for ML models.

Each strategy knows how to build features, train, evaluate, persist and load.
Used by ml_service (FastAPI side) and by Celery tasks (sync side); both call
the same pure-Python methods so behavior is identical.
"""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

CHARGER_TYPE_MAP = {"slow": 0, "fast": 1, "ultra_fast": 2}

DURATION_FEATURES = [
    "charger_type_code",
    "start_battery_percent",
    "end_battery_percent",
    "battery_capacity_kwh",
    "charging_power_kw",
    "temperature_c",
    "average_voltage",
    "average_current",
]


class ModelStrategy(ABC):
    name: str
    version_prefix: str

    @abstractmethod
    def train(self, df: pd.DataFrame) -> dict: ...

    @abstractmethod
    def artifact_name(self, version: str) -> str: ...


def _encode(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["charger_type_code"] = df["charger_type"].map(CHARGER_TYPE_MAP).fillna(0)
    return df


class RandomForestDurationStrategy(ModelStrategy):
    name = "duration"
    version_prefix = "rf_duration"

    def artifact_name(self, version: str) -> str:
        return f"{version}.joblib"

    def train(self, df: pd.DataFrame, artifacts_dir: str = "app/artifacts/models") -> dict:
        df = _encode(df)
        df = df[df["duration_minutes"] > 0]
        X = df[DURATION_FEATURES]
        y = df["duration_minutes"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        model = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = float(mean_absolute_error(y_test, preds))
        rmse = float(np.sqrt(np.mean((y_test.values - preds) ** 2)))
        r2 = float(r2_score(y_test, preds))

        version = f"{self.version_prefix}_{datetime.now(timezone.utc):%Y%m%d%H%M%S}"
        os.makedirs(artifacts_dir, exist_ok=True)
        path = os.path.join(artifacts_dir, self.artifact_name(version))
        joblib.dump(model, path)
        return {
            "model_type": self.name,
            "model_version": version,
            "artifact_path": path,
            "mae": mae,
            "rmse": rmse,
            "r2": r2,
            "training_rows": int(len(df)),
        }

    @staticmethod
    def predict(model, payload: dict) -> float:
        row = {
            "charger_type_code": CHARGER_TYPE_MAP.get(payload["charger_type"], 0),
            "start_battery_percent": payload["start_battery_percent"],
            "end_battery_percent": payload["end_battery_percent"],
            "battery_capacity_kwh": payload["battery_capacity_kwh"],
            "charging_power_kw": payload["charging_power_kw"],
            "temperature_c": payload["temperature_c"],
            "average_voltage": payload["average_voltage"],
            "average_current": payload["average_current"],
        }
        X = pd.DataFrame([row])[DURATION_FEATURES]
        return float(model.predict(X)[0])


class IsolationForestAnomalyStrategy(ModelStrategy):
    name = "anomaly"
    version_prefix = "iso_anomaly"

    def artifact_name(self, version: str) -> str:
        return f"{version}.joblib"

    def train(self, df: pd.DataFrame, artifacts_dir: str = "app/artifacts/models") -> dict:
        df = _encode(df)
        features = ["energy_kwh", "duration_minutes", "charging_power_kw",
                    "temperature_c", "average_voltage", "average_current"]
        X = df[features].fillna(0)
        model = IsolationForest(contamination=0.05, random_state=42)
        model.fit(X)
        version = f"{self.version_prefix}_{datetime.now(timezone.utc):%Y%m%d%H%M%S}"
        os.makedirs(artifacts_dir, exist_ok=True)
        path = os.path.join(artifacts_dir, self.artifact_name(version))
        joblib.dump({"model": model, "features": features}, path)
        return {
            "model_type": self.name,
            "model_version": version,
            "artifact_path": path,
            "mae": None,
            "rmse": None,
            "r2": None,
            "training_rows": int(len(df)),
        }
