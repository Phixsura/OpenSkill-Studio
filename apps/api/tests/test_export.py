"""Tests for app and installation export."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"exp-{uuid.uuid4().hex[:8]}@test.com"


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


async def _setup_installed(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Exp"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"exp-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Exp Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"expapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": "Export App",
            "slug": app_slug,
            "category": "connector",
            "description": "App for export testing",
        },
        headers=h,
    )
    app_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Export"},
                "permissions": ["read:cohorts"],
            },
            "content_hash": "a" * 64,
            "changelog": "Initial",
        },
        headers=h,
    )
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]
    return h, app_id, v_id, org_id, inst_id


@pytest.mark.asyncio
async def test_export_app(c):
    h, app_id, _, _, _ = await _setup_installed(c)
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["export_version"] == "1.0"
    assert data["app"]["name"] == "Export App"
    assert data["app"]["category"] in ("CONNECTOR", "connector")
    assert data["version_count"] == 1
    assert len(data["versions"]) == 1
    assert data["versions"][0]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_export_app_requires_ownership(c):
    h1, app_id, _, _, _ = await _setup_installed(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_id}/export", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_export_installation(c):
    h, app_id, v_id, org_id, inst_id = await _setup_installed(c)

    # Add some config
    await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"config": {"url": "https://lms.test"}},
        headers=h,
    )

    # Add secret
    await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "API_KEY", "value": "test-secret"},
        headers=h,
    )

    # Add event subscription
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )

    # Add rule
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Sync",
            "trigger_event": "submission.graded",
            "action_type": "webhook",
            "action_config": {"url": "https://lms.test/sync"},
        },
        headers=h,
    )

    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/export",
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["export_version"] == "1.0"
    assert data["installation"]["app_id"] == app_id
    assert data["installation"]["config"]["url"] == "https://lms.test"
    assert len(data["event_subscriptions"]) == 1
    assert data["event_subscriptions"][0]["event_type"] == "submission.completed"
    assert len(data["automation_rules"]) == 1
    assert data["automation_rules"][0]["name"] == "Sync"
    # Secret keys exported but NOT values
    assert len(data["secret_keys"]) == 1
    assert data["secret_keys"][0]["key"] == "API_KEY"


@pytest.mark.asyncio
async def test_export_installation_wrong_org(c):
    h, _, _, org_id, inst_id = await _setup_installed(c)
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org2_id = org2_r.json()["data"]["id"]
    r = await c.get(
        f"/api/v1/orgs/{org2_id}/apps/installations/{inst_id}/export",
        headers=h,
    )
    assert r.status_code == 404


def test_export_service_imports():
    from app.services.app_export import export_app_config, export_installation_config

    assert callable(export_app_config)
    assert callable(export_installation_config)
