"""Tests for app conformance suite and observability."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"conf-{uuid.uuid4().hex[:8]}@test.com"


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
    """Create auth + dev account + app + version → return (headers, app_data, org_id)."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Conf"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}

    # Developer account
    slug = f"dev-{uuid.uuid4().hex[:8]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Test Dev", "slug": slug, "support_email": f"{slug}@test.com"},
        headers=h,
    )

    # App
    app_slug = f"app-{uuid.uuid4().hex[:8]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={
            "name": f"Test App {app_slug}",
            "slug": app_slug,
            "category": "connector",
            "description": "Test conformance app",
        },
        headers=h,
    )
    app_data = r.json()["data"]

    # Version
    await c.post(
        f"/api/v1/developer/apps/{app_data['id']}/versions",
        json={
            "version": "1.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Test", "slug": app_slug, "version": "1.0.0", "category": "connector"},
                "permissions": ["read:cohorts", "subscribe:events"],
            },
            "content_hash": "a" * 64,
            "signature": "test-sig-placeholder",
        },
        headers=h,
    )

    # Org
    r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:8]}"}, headers=h)
    org_id = r.json()["data"]["id"]

    return h, app_data, org_id


# ── Conformance Tests ────────────────────────────────────


@pytest.mark.asyncio
async def test_conformance_suite_passes(c):
    h, app_data, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/conformance", headers=h)
    assert r.status_code == 200
    report = r.json()["data"]
    assert report["app_name"] == app_data["name"]
    assert report["version"] == "1.0.0"
    assert report["summary"]["total_checks"] > 0
    # Should pass — we have manifest, version, content_hash, signature
    assert report["summary"]["fail"] == 0


@pytest.mark.asyncio
async def test_conformance_checks_structure(c):
    h, app_data, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/conformance", headers=h)
    report = r.json()["data"]
    checks = report["checks"]
    # Verify check names cover all expected areas
    check_names = {ch["name"] for ch in checks}
    assert "manifest_present" in check_names
    assert "manifest_valid" in check_names
    assert "has_versions" in check_names
    assert "content_hash" in check_names
    assert "api_key_hygiene" in check_names


@pytest.mark.asyncio
async def test_conformance_requires_ownership(c):
    h1, app_data, _ = await _setup(c)
    # Second user
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/conformance", headers=h2)
    assert r.status_code == 403


# ── Observability Tests ──────────────────────────────────


@pytest.mark.asyncio
async def test_app_stats(c):
    h, app_data, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/stats", headers=h)
    assert r.status_code == 200
    stats = r.json()["data"]
    assert stats["app_id"] == app_data["id"]
    assert stats["versions"] >= 1
    assert "executions_24h" in stats
    assert "total" in stats["executions_24h"]


@pytest.mark.asyncio
async def test_install_breakdown(c):
    h, app_data, _ = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/installs/breakdown", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert "breakdown" in data


@pytest.mark.asyncio
async def test_org_app_stats(c):
    h, app_data, org_id = await _setup(c)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/stats", headers=h)
    assert r.status_code == 200
    stats = r.json()["data"]
    assert stats["org_id"] == org_id
    assert "installed_apps" in stats
    assert "executions_24h" in stats


# ── Manifest Validation API Tests ────────────────────────


@pytest.mark.asyncio
async def test_validate_manifest_endpoint_valid(c):
    h, _, _ = await _setup(c)
    r = await c.post(
        "/api/v1/developer/validate-manifest",
        json={
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Test", "slug": "test", "version": "1.0.0"},
                "permissions": ["read:cohorts"],
            }
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["valid"] is True
    assert data["error_count"] == 0


@pytest.mark.asyncio
async def test_validate_manifest_endpoint_invalid(c):
    h, _, _ = await _setup(c)
    r = await c.post(
        "/api/v1/developer/validate-manifest",
        json={
            "manifest": {
                "app": {"name": "Test"},
                "permissions": ["hack:system"],
            }
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["valid"] is False
    assert data["error_count"] >= 2  # missing schema_version + invalid permission
