"""Unit test for PredictionService: trains a model directly, then predicts and
checks a prediction log row is written. Exercises service + repository without
the HTTP layer."""
import pandas as pd

from app.models.ml_model import MLModelMetric
from app.patterns.data_generator_factory import DataGeneratorFactory
from app.patterns.model_strategy import RandomForestDurationStrategy
from app.patterns.unit_of_work import UnitOfWork
from app.services.prediction_service import PredictionService


async def _train_and_register(tmp_path):
    df = pd.DataFrame(DataGeneratorFactory.create(seed=1).generate(300))
    result = RandomForestDurationStrategy().train(df, artifacts_dir=str(tmp_path))
    async with UnitOfWork() as uow:
        await uow.ml.add(MLModelMetric(
            model_type=result["model_type"], model_version=result["model_version"],
            artifact_path=result["artifact_path"], mae=result["mae"],
            rmse=result["rmse"], r2=result["r2"], training_rows=result["training_rows"],
        ))
        await uow.commit()
    return result["model_version"]


async def test_predict_returns_positive_and_logs(engine, tmp_path):
    version = await _train_and_register(tmp_path)
    payload = {
        "charger_type": "fast", "start_battery_percent": 20, "end_battery_percent": 80,
        "battery_capacity_kwh": 64, "charging_power_kw": 50, "temperature_c": 20,
        "average_voltage": 400, "average_current": 125,
    }
    result = await PredictionService().predict_duration(payload, user_id=1)
    assert result["predicted_duration_minutes"] > 0
    assert result["model_version"] == version

    # a prediction log row must exist
    from sqlalchemy import select
    from app.models.prediction_log import PredictionLog
    async with UnitOfWork() as uow:
        rows = (await uow._session.execute(select(PredictionLog))).scalars().all()
    assert len(rows) == 1
    assert rows[0].user_id == 1
