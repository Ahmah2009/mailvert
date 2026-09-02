import pytest
from httpx import ASGITransport, AsyncClient

from mailvert.api.app import app


@pytest.mark.asyncio
async def test_healthz():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_verify_rejects_bad_syntax():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/verify", params={"email": "not-an-email"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "invalid"
    assert body["syntax_valid"] is False
