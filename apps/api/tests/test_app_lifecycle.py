"""Tests for app lifecycle, health monitoring, and version adoption."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"life-{uuid.uuid4().hex[:8]}@test.com"


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
    """Create auth + dev account + app + version."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Life"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}

    slug = f"life-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Life Dev", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )

    app_slug = f"lapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Life App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_data = r.json()["data"]

    # Create version
    r = await c.post(
        f"/api/v1/developer/apps/{app_data['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v1_id = r.json()["data"]["id"]

    return h, app_data, v1_id


@pytest.mark.asyncio
async def test_version_adoption_endpoint(c):
    h, app_data, v1_id = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/version-adoption", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["app_id"] == app_data["id"]
    assert isinstance(data["versions"], list)
    assert len(data["versions"]) >= 1
    assert data["versions"][0]["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_version_adoption_with_install(c):
    h, app_data, v1_id = await _setup(c)

    # Create org + install
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_data["id"], "app_version_id": v1_id},
        headers=h,
    )

    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/version-adoption", headers=h)
    assert r.status_code == 200
    versions = r.json()["data"]["versions"]
    v1 = next(v for v in versions if v["version"] == "1.0.0")
    assert v1["install_count"] == 1
    assert v1["adoption_pct"] == 100.0


@pytest.mark.asyncio
async def test_app_health_endpoint(c):
    h, app_data, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/health", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] == "unknown"  # no executions yet
    assert data["executions_24h"]["total"] == 0
    assert "version_adoption" in data


@pytest.mark.asyncio
async def test_health_requires_ownership(c):
    h1, app_data, _ = await _setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/health", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_version_adoption_requires_ownership(c):
    h1, app_data, _ = await _setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/version-adoption", headers=h2)
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_upgrade_moves_to_latest(c):
    h, app_data, v1_id = await _setup(c)

    # Install on v1
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_data["id"], "app_version_id": v1_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    # Create v2
    r = await c.post(
        f"/api/v1/developer/apps/{app_data['id']}/versions",
        json={
            "version": "2.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "b" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    # Upgrade
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["app_version_id"] == v2_id


@pytest.mark.asyncio
async def test_upgrade_noop_when_latest(c):
    h, app_data, v1_id = await _setup(c)

    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_data["id"], "app_version_id": v1_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]

    # Upgrade when already on latest — should be a noop
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/upgrade", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["app_version_id"] == v1_id


# ── Lifecycle service unit tests ─────────────────────────


def test_lifecycle_imports():
    from app.services.app_lifecycle import (
        auto_upgrade_installations,
        check_app_health,
        get_deprecation_info,
        get_version_adoption,
    )

    assert callable(get_deprecation_info)
    assert callable(auto_upgrade_installations)
    assert callable(get_version_adoption)
    assert callable(check_app_health)
