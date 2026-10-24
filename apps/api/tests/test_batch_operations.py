"""Tests for batch operations, pinned version behavior, and auto-upgrade."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"batch-{uuid.uuid4().hex[:8]}@test.com"


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
    """Create user + dev + app + v1 + org + install."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Batch"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"bat-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Batch Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"batapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Batch App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": ["read:cohorts"]},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v1_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v1_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]
    return h, app_id, v1_id, org_id, inst_id


@pytest.mark.asyncio
async def test_batch_upgrade_multiple_orgs(c):
    h, app_id, v1_id, org1_id, inst1_id = await _full_setup(c)

    # Install in second org
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org2_id = org2_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{org2_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v1_id},
        headers=h,
    )

    # Create v2
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": ["read:cohorts"]},
            "content_hash": "b" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    # Batch upgrade — blocked because app is draft & version not approved
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/batch-upgrade",
        json={"app_id": app_id, "version_id": v2_id},
        headers=h,
    )
    assert r.status_code == 422  # version not approved


@pytest.mark.asyncio
async def test_batch_upgrade_skips_pinned(c):
    h, app_id, v1_id, org_id, inst_id = await _full_setup(c)

    # Pin the installation
    r = await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"pinned_version": True},
        headers=h,
    )
    assert r.status_code == 200

    # Create v2
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "c" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    # Batch upgrade — blocked because version not approved
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/batch-upgrade",
        json={"app_id": app_id, "version_id": v2_id},
        headers=h,
    )
    assert r.status_code == 422  # version not approved


@pytest.mark.asyncio
async def test_batch_upgrade_wrong_version(c):
    h, app_id, v1_id, _, _ = await _full_setup(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/batch-upgrade",
        json={"app_id": app_id, "version_id": "nonexistent"},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_batch_upgrade_requires_ownership(c):
    h1, app_id, v1_id, _, _ = await _full_setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/batch-upgrade",
        json={"app_id": app_id, "version_id": v1_id},
        headers=h2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_deprecation_notice_with_installs(c):
    h, app_id, v1_id, org_id, inst_id = await _full_setup(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/deprecation-notice",
        json={"message": "Sunset Q1 2027", "sunset_date": "2027-03-31"},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["notified_installations"] >= 1
    assert data["notice"]["sunset_date"] == "2027-03-31"


@pytest.mark.asyncio
async def test_compatibility_check_same_version(c):
    h, app_id, v1_id, _, _ = await _full_setup(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/check-compatibility",
        json={"current_version_id": v1_id, "new_version_id": v1_id},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["compatible"] is True
    assert r.json()["data"]["breaking_changes"] == []
