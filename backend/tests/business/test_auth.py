import pytest


async def _register(client, email="a@b.com", pw="secret123"):
    return await client.post("/auth/register", json={"email": email, "password": pw, "full_name": "A"})


async def test_register_and_login(client):
    r = await _register(client)
    assert r.status_code == 201
    assert r.json()["email"] == "a@b.com"

    r = await client.post("/auth/login", json={"email": "a@b.com", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


async def test_protected_route_rejects_anon(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401


async def test_protected_route_with_token(client):
    await _register(client)
    token = (await client.post("/auth/login", json={"email": "a@b.com", "password": "secret123"})).json()["access_token"]
    r = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200


async def test_invalid_token(client):
    r = await client.get("/auth/me", headers={"Authorization": "Bearer nonsense"})
    assert r.status_code == 401


async def test_login_rate_limit(client):
    await _register(client)
    codes = []
    for _ in range(7):
        rr = await client.post("/auth/login", json={"email": "a@b.com", "password": "wrong"})
        codes.append(rr.status_code)
    assert 429 in codes
