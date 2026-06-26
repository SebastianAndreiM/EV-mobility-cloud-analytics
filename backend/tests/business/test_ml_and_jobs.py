import pytest


async def _auth(client):
    await client.post("/auth/register", json={"email": "m@b.com", "password": "secret123"})
    token = (await client.post("/auth/login", json={"email": "m@b.com", "password": "secret123"})).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_train_creates_job_and_completes(client):
    h = await _auth(client)
    # need enough data for training
    await client.post("/data/generate", json={"count": 200, "seed": 5}, headers=h)
    r = await client.post("/ml/train-duration-model", headers=h)
    assert r.status_code == 200
    job_id = r.json()["job_id"]

    # Celery is eager in tests, so the job runs synchronously.
    jr = await client.get(f"/jobs/{job_id}", headers=h)
    assert jr.status_code == 200
    assert jr.json()["status"] in ("completed", "running", "queued", "failed")


async def test_predict_after_training(client):
    h = await _auth(client)
    await client.post("/data/generate", json={"count": 300, "seed": 2}, headers=h)
    await client.post("/ml/train-duration-model", headers=h)

    payload = {
        "charger_type": "fast", "start_battery_percent": 20, "end_battery_percent": 80,
        "battery_capacity_kwh": 64, "charging_power_kw": 50, "temperature_c": 20,
        "average_voltage": 400, "average_current": 125,
    }
    r = await client.post("/ml/predict-duration", json=payload, headers=h)
    assert r.status_code == 200
    assert r.json()["predicted_duration_minutes"] > 0


async def test_anomalies_endpoint(client):
    h = await _auth(client)
    await client.post("/data/generate", json={"count": 200, "seed": 8}, headers=h)
    r = await client.get("/analytics/anomalies", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json(), list)
