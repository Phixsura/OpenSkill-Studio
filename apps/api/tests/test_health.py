import pytest


@pytest.mark.asyncio
async def test_liveness_returns_ok(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_response_schema(client):
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert isinstance(data["status"], str)


@pytest.mark.asyncio
async def test_404_returns_error_envelope(client):
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code in (404, 405)
    data = response.json()
    assert "error" in data
    assert "code" in data["error"]
