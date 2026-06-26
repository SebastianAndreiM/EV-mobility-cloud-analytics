"""Unit tests for ML strategies (Strategy Pattern). Pure sklearn, no DB."""
import os

import joblib
import pandas as pd

from app.patterns.data_generator_factory import DataGeneratorFactory
from app.patterns.model_strategy import (
    IsolationForestAnomalyStrategy, RandomForestDurationStrategy,
)


def _df(n=300, seed=1):
    return pd.DataFrame(DataGeneratorFactory.create(seed=seed).generate(n))


def test_duration_strategy_trains_and_reports_metrics(tmp_path):
    result = RandomForestDurationStrategy().train(_df(), artifacts_dir=str(tmp_path))
    assert result["model_type"] == "duration"
    assert result["training_rows"] > 0
    assert result["mae"] is not None and result["mae"] >= 0
    assert result["rmse"] is not None
    assert os.path.exists(result["artifact_path"])


def test_duration_strategy_predict_is_positive(tmp_path):
    result = RandomForestDurationStrategy().train(_df(), artifacts_dir=str(tmp_path))
    model = joblib.load(result["artifact_path"])
    payload = {
        "charger_type": "fast", "start_battery_percent": 20, "end_battery_percent": 80,
        "battery_capacity_kwh": 64, "charging_power_kw": 50, "temperature_c": 20,
        "average_voltage": 400, "average_current": 125,
    }
    pred = RandomForestDurationStrategy.predict(model, payload)
    assert pred > 0


def test_anomaly_strategy_trains_and_saves(tmp_path):
    result = IsolationForestAnomalyStrategy().train(_df(), artifacts_dir=str(tmp_path))
    assert result["model_type"] == "anomaly"
    saved = joblib.load(result["artifact_path"])
    assert "model" in saved and "features" in saved


def test_artifact_name_versioned():
    s = RandomForestDurationStrategy()
    name = s.artifact_name("rf_duration_123")
    assert name.endswith(".joblib")
