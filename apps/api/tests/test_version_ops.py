"""Tests for version operations — rollback, pin, unpin."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"vops-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "VOps"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"vop-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "VOps Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"vopapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "VOps App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    # v1
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v1_id = r.json()["data"]["id"]

    # v2
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "b" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    # org + install on v2
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v2_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]
    return h, app_id, v1_id, v2_id, org_id, inst_id


@pytest.mark.asyncio
async def test_rollback_to_previous_version(c):
    h, app_id, v1_id, v2_id, org_id, inst_id = await _setup(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback",
        json={"target_version_id": v1_id},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["app_version_id"] == v1_id


@pytest.mark.asyncio
async def test_rollback_wrong_app_version(c):
    h, app_id, v1_id, v2_id, org_id, inst_id = await _setup(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback",
        json={"target_version_id": "nonexistent-version"},
        headers=h,
    )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_pin_version(c):
    h, _, _, _, org_id, inst_id = await _setup(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/pin",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["pinned_version"] is True


@pytest.mark.asyncio
async def test_unpin_version(c):
    h, _, _, _, org_id, inst_id = await _setup(c)
    # Pin first
    await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/pin", headers=h)
    # Unpin
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/unpin",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["pinned_version"] is False


@pytest.mark.asyncio
async def test_rollback_requires_org_membership(c):
    h1, app_id, v1_id, v2_id, org_id, inst_id = await _setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rollback",
        json={"target_version_id": v1_id},
        headers=h2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_pin_wrong_org(c):
    h, _, _, _, org_id, inst_id = await _setup(c)
    # Create second org
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org2_id = org2_r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{org2_id}/apps/installations/{inst_id}/pin",
        headers=h,
    )
    assert r.status_code == 404
