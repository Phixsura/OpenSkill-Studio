"""Roundtrip test — export then validate import."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.app_import import validate_import_data


def _email():
    return f"rt-{uuid.uuid4().hex[:8]}@test.com"


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


@pytest.mark.asyncio
async def test_export_import_roundtrip(c):
    """Export an app, then validate the exported data for import."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "RT"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"rt-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "RT Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)

    app_slug = f"rtapp-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={
        "name": "Roundtrip App", "slug": app_slug, "category": "connector", "description": "Test export/import",
    }, headers=h)
    app_id = r.json()["data"]["id"]

    await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0",
        "manifest": {"schema_version": "1.0", "app": {"name": "RT"}, "permissions": ["read:cohorts"]},
        "content_hash": "a" * 64, "changelog": "v1",
    }, headers=h)

    # Export
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    assert r.status_code == 200
    exported = r.json()["data"]

    # Validate for import
    result = validate_import_data(exported)
    assert result["valid"] is True, f"Import validation failed: {result['errors']}"
    assert result["errors"] == []


@pytest.mark.asyncio
async def test_export_installation_roundtrip(c):
    """Export installation config, verify structure."""
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "RT2"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"rt2-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "RT2 Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)

    app_slug = f"rt2app-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "RT2 App", "slug": app_slug, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "b" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]

    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    inst_id = ir.json()["data"]["id"]

    # Add config + secret + event
    await c.patch(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}", json={"config": {"url": "https://test.com"}}, headers=h)
    await c.put(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets", json={"key": "KEY", "value": "secret"}, headers=h)
    await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={"event_type": "submission.completed"}, headers=h)

    # Export
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/export", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["installation"]["config"]["url"] == "https://test.com"
    assert len(data["event_subscriptions"]) == 1
    assert len(data["secret_keys"]) == 1
    assert data["secret_keys"][0]["key"] == "KEY"
