"""Tests for installation detail operations — config, secrets, events, rules, execution."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"inst-{uuid.uuid4().hex[:8]}@test.com"


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


async def _full_install(c):
    """Full setup: user + dev + app + version + org + installation."""
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Inst"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"inst-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Inst Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"instapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Inst App", "slug": app_slug, "category": "connector"},
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
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v_id, "granted_permissions": ["read:cohorts"]},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]
    return h, app_id, v_id, org_id, inst_id


# ── Config ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_installation_config(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    r = await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"config": {"base_url": "https://lms.example.com", "sync_interval": 60}},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["config"]["base_url"] == "https://lms.example.com"


@pytest.mark.asyncio
async def test_update_granted_permissions(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    r = await c.patch(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}",
        json={"granted_permissions": ["read:cohorts", "read:projects"]},
        headers=h,
    )
    assert r.status_code == 200
    assert "read:projects" in r.json()["data"]["granted_permissions"]


# ── Secrets ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_and_update_secret(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    # Set
    r = await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "API_KEY", "value": "secret-v1", "description": "First key"},
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["key"] == "API_KEY"

    # Update (same key) — upsert
    r = await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "API_KEY", "value": "secret-v2", "description": "Updated"},
        headers=h,
    )
    assert r.status_code == 200, f"Update failed: {r.json()}"

    # List — should have 1 secret (upserted)
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        headers=h,
    )
    assert r.status_code == 200
    assert len(r.json()["data"]) == 1


@pytest.mark.asyncio
async def test_multiple_secrets(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    for key in ["KEY_A", "KEY_B", "KEY_C"]:
        r = await c.put(
            f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
            json={"key": key, "value": f"value-{key}"},
            headers=h,
        )
        assert r.status_code == 200

    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        headers=h,
    )
    assert len(r.json()["data"]) == 3


@pytest.mark.asyncio
async def test_delete_secret(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    await c.put(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        json={"key": "TEMP_KEY", "value": "temp"},
        headers=h,
    )
    r = await c.delete(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets/TEMP_KEY",
        headers=h,
    )
    assert r.status_code == 200
    # Verify deleted
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/secrets",
        headers=h,
    )
    assert len(r.json()["data"]) == 0


# ── Event Subscriptions ──────────────────────────────────


@pytest.mark.asyncio
async def test_multiple_event_subscriptions(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    events = ["submission.completed", "cohort.member_added", "project.published"]
    for evt in events:
        r = await c.post(
            f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
            json={"event_type": evt},
            headers=h,
        )
        assert r.status_code == 200

    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        headers=h,
    )
    assert len(r.json()["data"]) == 3


@pytest.mark.asyncio
async def test_duplicate_event_subscription_rejected(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events",
        json={"event_type": "submission.completed"},
        headers=h,
    )
    assert r.status_code == 409


# ── Automation Rules ─────────────────────────────────────


@pytest.mark.asyncio
async def test_create_webhook_rule(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Grade Sync",
            "trigger_event": "submission.graded",
            "action_type": "webhook",
            "action_config": {"url": "https://lms.example.com/api/sync", "method": "POST"},
        },
        headers=h,
    )
    assert r.status_code == 200
    rule = r.json()["data"]
    assert rule["name"] == "Grade Sync"
    assert rule["enabled"] is True
    assert rule["execution_count"] == 0


@pytest.mark.asyncio
async def test_create_notification_rule(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules",
        json={
            "name": "Alert on fail",
            "trigger_event": "evaluation.failed",
            "action_type": "notification",
            "action_config": {"message": "Evaluation failed!"},
            "max_executions_per_hour": 10,
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["max_executions_per_hour"] == 10


# ── Execution Log ────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_executions_empty(c):
    h, _, _, org_id, inst_id = await _full_install(c)
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/executions",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"] == []
    assert r.json()["meta"]["total"] == 0
