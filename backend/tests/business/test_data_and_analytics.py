import pytest


async def _auth(client):
    await client.post("/auth/register", json={"email": "d@b.com", "password": "secret123"})
    token = (await client.post("/auth/login", json={"email": "d@b.com", "password": "secret123"})).json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


async def test_generate_creates_sessions(client):
    h = await _auth(client)
    r = await client.post("/data/generate", json={"count": 50, "seed": 7}, headers=h)
    assert r.status_code == 200
    assert r.json()["generated"] == 50

    r = await client.get("/data/sessions?page=1&page_size=10", headers=h)
    assert r.json()["total"] == 50


async def test_sessions_respect_business_constraints(client):
    h = await _auth(client)
    await client.post("/data/generate", json={"count": 100, "seed": 1}, headers=h)
    r = await client.get("/data/sessions?page=1&page_size=100", headers=h)
    for s in r.json()["items"]:
        assert s["start_battery_percent"] < s["end_battery_percent"]
        assert s["duration_minutes"] > 0
        assert s["energy_kwh"] > 0
        assert -10 <= s["temperature_c"] <= 45


async def test_summary_matches_db(client):
    h = await _auth(client)
    await client.post("/data/generate", json={"count": 40, "seed": 3}, headers=h)
    r = await client.get("/analytics/summary", headers=h)
    body = r.json()
    assert body["total_sessions"] == 40
    assert 0 <= body["anomaly_rate"] <= 1


async def test_deterministic_seed(client):
    h = await _auth(client)
    await client.post("/data/generate", json={"count": 10, "seed": 99}, headers=h)
    first = (await client.get("/analytics/summary", headers=h)).json()["total_energy"]
    await client.delete("/data/sessions", headers=h)
    await client.post("/data/generate", json={"count": 10, "seed": 99}, headers=h)
    second = (await client.get("/analytics/summary", headers=h)).json()["total_energy"]
    assert first == second
