"""Tests for app usage metering and additional observability endpoints."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"usage-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Usage"},
    )
    d = r.json()
    h = {"Authorization": f"Bearer {d['access_token']}"}
    slug = f"usg-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Usage Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"usgapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Usage App", "slug": app_slug, "category": "analytics"},
        headers=h,
    )
    return h, r.json()["data"]


@pytest.mark.asyncio
async def test_app_usage_endpoint(c):
    h, app_data = await _setup(c)
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/usage", headers=h)
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["app_id"] == app_data["id"]
    assert "usage" in data


@pytest.mark.asyncio
async def test_app_usage_requires_ownership(c):
    h1, app_data = await _setup(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.get(f"/api/v1/developer/apps/{app_data['id']}/usage", headers=h2)
    assert r.status_code == 403


def test_usage_service_import():
    from app.services.app_usage import (
        APP_USAGE_TYPES,
        get_app_usage_summary,
        get_installation_usage_summary,
        record_app_usage,
    )

    assert callable(record_app_usage)
    assert callable(get_app_usage_summary)
    assert callable(get_installation_usage_summary)
    assert len(APP_USAGE_TYPES) == 5


def test_app_search_import():
    from app.services.app_search import search_marketplace_apps

    assert callable(search_marketplace_apps)


def test_app_lifecycle_import():
    from app.services.app_lifecycle import (
        auto_upgrade_installations,
        check_app_health,
        get_deprecation_info,
        get_version_adoption,
    )

    assert callable(auto_upgrade_installations)
    assert callable(check_app_health)
    assert callable(get_deprecation_info)
    assert callable(get_version_adoption)


def test_event_hooks_complete():
    """Verify all event hooks are defined."""
    from app.services.app_event_hooks import (
        on_app_installed,
        on_app_uninstalled,
        on_cohort_member_added,
        on_cohort_member_removed,
        on_evaluation_completed,
        on_org_member_added,
        on_pack_installed,
        on_pack_published,
        on_project_published,
        on_submission_completed,
        on_submission_graded,
        on_workflow_run_completed,
    )

    hooks = [
        on_submission_completed, on_submission_graded,
        on_cohort_member_added, on_cohort_member_removed,
        on_project_published, on_pack_published, on_pack_installed,
        on_workflow_run_completed, on_app_installed, on_app_uninstalled,
        on_evaluation_completed, on_org_member_added,
    ]
    assert len(hooks) == 12
    assert all(callable(h) for h in hooks)
