"""Tests for webhook delivery log and developer tools endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"wh-{uuid.uuid4().hex[:8]}@test.com"


@pytest_asyncio.fixture
async def c():
    from app.main import app

    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager

    from app.core.database import engine

    @asynccontextmanager
    async def _noop(a):
        yield

    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()


async def _setup(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "WH"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}
    slug = f"wh-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "WH Dev", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )
    app_slug = f"whapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "WH App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]
    return h, app_id


@pytest.mark.asyncio
async def test_webhook_deliveries_empty(c):
    h, app_id = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/webhook-deliveries", headers=h)
    assert r.status_code == 200
    assert r.json()["data"] == []
    assert r.json()["meta"]["total"] == 0


@pytest.mark.asyncio
async def test_webhook_delivery_stats_empty(c):
    h, app_id = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/webhook-deliveries/stats", headers=h)
    assert r.status_code == 200
    stats = r.json()["data"]
    assert stats["total"] == 0
    assert stats["avg_duration_ms"] == 0


@pytest.mark.asyncio
async def test_webhook_deliveries_requires_ownership(c):
    h1, app_id = await _setup(c)
    # Second user
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_id}/webhook-deliveries", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_developer_tools_event_types(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/event-types", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 30
    assert "submission" in data["categories"]
    assert "marketplace" in data["categories"]
    assert "app" in data["categories"]


@pytest.mark.asyncio
async def test_developer_tools_permissions(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/permissions", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] >= 30
    assert "read" in data["categories"]
    assert "write" in data["categories"]
    assert "subscribe" in data["categories"]


@pytest.mark.asyncio
async def test_developer_tools_ui_surfaces(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["total"] == 8
    surfaces = [s["id"] for s in data["surfaces"]]
    assert "dashboard_card" in surfaces
    assert "operator_console" in surfaces


@pytest.mark.asyncio
async def test_developer_tools_fixtures(c):
    h, _ = await _setup(c)
    r = await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)
    assert r.status_code == 200
    fixtures = r.json()["data"]
    assert "cohort" in fixtures
    assert "project" in fixtures
    assert "submission" in fixtures
    assert "user" in fixtures
    assert "organization" in fixtures
    assert "event_payload" in fixtures
    assert "submission.completed" in fixtures["event_payload"]


@pytest.mark.asyncio
async def test_developer_tools_validate_valid(c):
    h, _ = await _setup(c)
    r = await c.post(
        "/api/v1/developer/tools/validate",
        json={
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Test", "slug": "test-app", "version": "1.0.0"},
                "permissions": ["read:cohorts"],
            }
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["valid"] is True


@pytest.mark.asyncio
async def test_developer_tools_validate_invalid(c):
    h, _ = await _setup(c)
    r = await c.post(
        "/api/v1/developer/tools/validate",
        json={"manifest": {"permissions": ["hack:system"]}},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["valid"] is False
    assert r.json()["data"]["error_count"] >= 2


@pytest.mark.asyncio
async def test_developer_tools_send_test_event(c):
    h, _ = await _setup(c)
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post(
        "/api/v1/developer/tools/send-test-event",
        json={
            "event_type": "submission.completed",
            "data": {"test_key": "test_value"},
            "org_id": org_id,
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["test"] is True


@pytest.mark.asyncio
async def test_developer_tools_send_invalid_event(c):
    h, _ = await _setup(c)
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    r = await c.post(
        "/api/v1/developer/tools/send-test-event",
        json={"event_type": "invalid.event.type", "org_id": org_id},
        headers=h,
    )
    assert r.status_code == 422


@pytest.mark.asyncio
async def test_adapter_registry_empty(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/adapters", headers=h)
    assert r.status_code == 200
    # May have adapters registered from other tests
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_source_registry_empty(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/sources", headers=h)
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_adapter_not_found(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/adapters/nonexistent-adapter", headers=h)
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_source_not_found(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/sources/nonexistent-source", headers=h)
    assert r.status_code == 404
