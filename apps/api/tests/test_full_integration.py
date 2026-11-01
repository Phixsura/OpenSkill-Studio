"""Full integration tests — cross-cutting scenarios that span multiple services."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"intg-{uuid.uuid4().hex[:8]}@test.com"


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


async def _full_setup(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Intg"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"intg-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Intg Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    return h, slug


@pytest.mark.asyncio
async def test_create_app_get_stats_conformance(c):
    """Create an app, check stats, run conformance — integrated flow."""
    h, _ = await _full_setup(c)
    app_slug = f"iapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Integrated App", "slug": app_slug, "category": "automation"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    # Create version with full manifest
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Integrated", "version": "1.0.0"},
                "permissions": ["read:cohorts", "subscribe:events"],
            },
            "content_hash": "a" * 64,
            "signature": "test-sig",
        },
        headers=h,
    )
    assert r.status_code == 200

    # Check stats
    r = await c.get(f"/api/v1/developer/apps/{app_id}/stats", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["versions"] == 1

    # Run conformance
    r = await c.get(f"/api/v1/developer/apps/{app_id}/conformance", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["summary"]["fail"] == 0

    # Check health
    r = await c.get(f"/api/v1/developer/apps/{app_id}/health", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "unknown"  # no executions

    # Analytics summary
    r = await c.get(f"/api/v1/developer/apps/{app_id}/analytics/summary", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["versions"] == 1

    # Version adoption
    r = await c.get(f"/api/v1/developer/apps/{app_id}/version-adoption", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]["versions"]) == 1


@pytest.mark.asyncio
async def test_install_configure_subscribe_execute(c):
    """Full installation lifecycle: install → config → secret → subscribe → execute."""
    h, _ = await _full_setup(c)
    app_slug = f"inst-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Install Flow", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": ["read:cohorts"]},
            "content_hash": "b" * 64,
        },
        headers=h,
    )
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]

    # Install
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v_id},
        headers=h,
    )
    inst_id = r.json()["data"]["id"]

    # Configure
    r = await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"config": {"api_url": "https://lms.example.com"}},
        headers=h,
    )
    assert r.status_code == 200

    # Set secret
    r = await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "API_KEY", "value": "test-key-123"},
        headers=h,
    )
    assert r.status_code == 200

    # Subscribe to event
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )
    assert r.status_code == 200

    # Create rule
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Auto sync",
            "trigger_event": "submission.graded",
            "action_type": "webhook",
            "action_config": {"url": "https://lms.example.com/sync"},
        },
        headers=h,
    )
    assert r.status_code == 200

    # Execute function
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute",
        json={"function_name": "on_submit", "payload": {"test": True}},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["success"] is True

    # Check execution log
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/executions",
        headers=h,
    )
    assert r.json()["meta"]["total"] >= 1

    # Org stats
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/stats", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["installed_apps"] == 1


@pytest.mark.asyncio
async def test_multiple_versions_compatibility_upgrade(c):
    """Create v1 → v2 → check compatibility → upgrade → rollback."""
    h, _ = await _full_setup(c)
    app_slug = f"ver-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Version Flow", "slug": app_slug, "category": "analytics"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    # v1
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": ["read:cohorts"]},
            "content_hash": "c" * 64,
        },
        headers=h,
    )
    v1_id = r.json()["data"]["id"]

    # v2 with new permission
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {},
                "permissions": ["read:cohorts", "write:projects"],
            },
            "content_hash": "d" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    # Check compatibility
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/check-compatibility",
        json={"current_version_id": v1_id, "new_version_id": v2_id},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["compatible"] is True
    assert "write:projects" in r.json()["data"]["permissions_added"]

    # Install v1
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v1_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    # Upgrade to v2
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["app_version_id"] == v2_id

    # Rollback to v1
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback",
        json={"target_version_id": v1_id},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["app_version_id"] == v1_id

    # Version adoption
    r = await c.get(f"/api/v1/developer/apps/{app_id}/version-adoption", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]["versions"]) == 2


@pytest.mark.asyncio
async def test_api_key_lifecycle(c):
    """Create key → use key → list keys → revoke → verify rejected."""
    h, slug = await _full_setup(c)
    app_slug = f"key-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Key Flow", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    # Create key
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/api-keys",
        json={"name": "Flow Key", "scopes": ["read:cohorts"]},
        headers=h,
    )
    assert r.status_code == 200
    key = r.json()["data"]["key"]
    key_id = r.json()["data"]["id"]

    # Use key to read account
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {key}"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["slug"] == slug

    # List keys
    r = await c.get(f"/api/v1/developer/apps/{app_id}/api-keys", headers=h)
    assert len(r.json()["data"]) == 1

    # Revoke
    r = await c.delete(f"/api/v1/developer/apps/{app_id}/api-keys/{key_id}", headers=h)
    assert r.status_code == 200

    # Verify rejected
    r = await c.get(
        "/api/v1/developer/accounts/me",
        headers={"Authorization": f"Bearer {key}"},
    )
    assert r.status_code == 401
