"""Tests for app compatibility checking, batch operations, and version rollback."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.services.app_compatibility import (
    PLATFORM_VERSION,
    check_upgrade_compatibility,
    is_compatible,
    parse_semver,
)


# ── Semver parsing ───────────────────────────────────────


def test_parse_semver_valid():
    assert parse_semver("1.0.0") == (1, 0, 0)
    assert parse_semver("2.3.4") == (2, 3, 4)
    assert parse_semver("10.20.30") == (10, 20, 30)
    assert parse_semver("1.0.0-beta.1") == (1, 0, 0)


def test_parse_semver_invalid():
    assert parse_semver("not-a-version") is None
    assert parse_semver("1.0") is None
    assert parse_semver("") is None


# ── Platform compatibility ───────────────────────────────


def test_is_compatible_no_minimum():
    assert is_compatible(None) is True
    assert is_compatible("") is True


def test_is_compatible_current():
    assert is_compatible(PLATFORM_VERSION) is True


def test_is_compatible_older():
    assert is_compatible("0.1.0") is True


def test_is_compatible_future():
    assert is_compatible("99.0.0") is False


# ── Upgrade compatibility ────────────────────────────────


def test_compatible_no_changes():
    m = {"permissions": ["read:cohorts"], "schema_version": "1.0"}
    report = check_upgrade_compatibility(m, m)
    assert report["compatible"] is True
    assert report["breaking_changes"] == []


def test_permissions_added():
    old = {"permissions": ["read:cohorts"]}
    new = {"permissions": ["read:cohorts", "write:projects"]}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is True
    assert "write:projects" in report["permissions_added"]
    assert len(report["warnings"]) > 0


def test_permissions_removed():
    old = {"permissions": ["read:cohorts", "write:projects"]}
    new = {"permissions": ["read:cohorts"]}
    report = check_upgrade_compatibility(old, new)
    assert "write:projects" in report["permissions_removed"]


def test_schema_version_major_breaking():
    old = {"schema_version": "1.0", "permissions": []}
    new = {"schema_version": "2.0", "permissions": []}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is False
    assert any("Schema version" in bc for bc in report["breaking_changes"])


def test_schema_version_minor_ok():
    old = {"schema_version": "1.0", "permissions": []}
    new = {"schema_version": "1.1", "permissions": []}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is True


def test_ui_surface_removed_breaking():
    old = {
        "permissions": [],
        "ui_extensions": [{"surface": "dashboard_card"}, {"surface": "cohort_tool"}],
    }
    new = {
        "permissions": [],
        "ui_extensions": [{"surface": "dashboard_card"}],
    }
    report = check_upgrade_compatibility(old, new)
    assert any("cohort_tool" in bc for bc in report["breaking_changes"])


def test_event_subscription_removed_warning():
    old = {"permissions": [], "event_subscriptions": ["submission.completed", "pack.published"]}
    new = {"permissions": [], "event_subscriptions": ["submission.completed"]}
    report = check_upgrade_compatibility(old, new)
    assert any("pack.published" in w for w in report["warnings"])


def test_new_required_secret_warning():
    old = {"permissions": [], "secrets": []}
    new = {
        "permissions": [],
        "secrets": [{"key": "NEW_KEY", "required": True}],
    }
    report = check_upgrade_compatibility(old, new)
    assert any("NEW_KEY" in w for w in report["warnings"])


def test_platform_version_incompatible():
    old = {"permissions": [], "app": {}}
    new = {"permissions": [], "app": {"min_platform_version": "99.0.0"}}
    report = check_upgrade_compatibility(old, new)
    assert report["compatible"] is False
    assert any("platform" in bc.lower() for bc in report["breaking_changes"])


def test_none_manifests():
    report = check_upgrade_compatibility(None, None)
    assert report["compatible"] is True
    report = check_upgrade_compatibility(None, {"permissions": []})
    assert report["compatible"] is True


# ── API integration tests ────────────────────────────────


def _email():
    return f"compat-{uuid.uuid4().hex[:8]}@test.com"


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


async def _setup_with_versions(c):
    """Create dev + app + 2 versions."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Compat"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"cmp-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Compat Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"cmpapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Compat App", "slug": app_slug, "category": "connector"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]

    # v1
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Compat"},
                "permissions": ["read:cohorts", "read:projects"],
                "event_subscriptions": ["submission.completed"],
            },
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v1_id = r.json()["data"]["id"]

    # v2 with added permission
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "2.0.0",
            "manifest": {
                "schema_version": "1.0",
                "app": {"name": "Compat"},
                "permissions": ["read:cohorts", "read:projects", "write:projects"],
                "event_subscriptions": ["submission.completed"],
            },
            "content_hash": "b" * 64,
        },
        headers=h,
    )
    v2_id = r.json()["data"]["id"]

    return h, app_id, v1_id, v2_id


@pytest.mark.asyncio
async def test_check_compatibility_endpoint(c):
    h, app_id, v1_id, v2_id = await _setup_with_versions(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/check-compatibility",
        json={"current_version_id": v1_id, "new_version_id": v2_id},
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["from_version"] == "1.0.0"
    assert data["to_version"] == "2.0.0"
    assert data["compatible"] is True
    assert "write:projects" in data["permissions_added"]


@pytest.mark.asyncio
async def test_batch_upgrade_endpoint(c):
    h, app_id, v1_id, v2_id = await _setup_with_versions(c)

    # Install on v1
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v1_id},
        headers=h,
    )

    # Batch upgrade — blocked because version not approved + app not published
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/batch-upgrade",
        json={"app_id": app_id, "version_id": v2_id},
        headers=h,
    )
    assert r.status_code == 422  # version not approved


@pytest.mark.asyncio
async def test_deprecation_notice_endpoint(c):
    h, app_id, _, _ = await _setup_with_versions(c)
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/deprecation-notice",
        json={
            "message": "This app is being sunset.",
            "sunset_date": "2027-01-01",
            "migration_guide_url": "https://example.com/migrate",
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["notice"]["sunset_date"] == "2027-01-01"
