"""Advanced event subscription and automation rule tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"ev-{uuid.uuid4().hex[:8]}@test.com"

@pytest_asyncio.fixture
async def c():
    from app.main import app
    orig = app.router.lifespan_context
    from contextlib import asynccontextmanager
    from app.core.database import engine
    @asynccontextmanager
    async def _noop(a): yield
    app.router.lifespan_context = _noop
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.router.lifespan_context = orig
    await engine.dispose()

async def _installed(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "EV"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"ev-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "EV Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"evapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "EV App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/versions", json={
        "version": "1.0.0", "manifest": {"schema_version": "1.0", "app": {}, "permissions": []}, "content_hash": "a" * 64,
    }, headers=h)
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(f"/api/v1/orgs/{org_id}/apps/install", json={"app_id": app_id, "app_version_id": v_id}, headers=h)
    return h, org_id, ir.json()["data"]["id"]

@pytest.mark.asyncio
async def test_subscribe_multiple_events(c):
    h, org_id, inst_id = await _installed(c)
    events = ["submission.completed", "cohort.member_added", "project.published", "pack.installed"]
    for ev in events:
        r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={"event_type": ev}, headers=h)
        assert r.status_code == 200
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", headers=h)
    assert len(r.json()["data"]) == 4

@pytest.mark.asyncio
async def test_duplicate_subscription_rejected(c):
    h, org_id, inst_id = await _installed(c)
    await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={"event_type": "submission.completed"}, headers=h)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={"event_type": "submission.completed"}, headers=h)
    assert r.status_code == 409

@pytest.mark.asyncio
async def test_delete_subscription(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events", json={"event_type": "pack.published"}, headers=h)
    sub_id = r.json()["data"]["id"]
    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/events/{sub_id}", headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_create_webhook_rule(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules", json={
        "name": "Sync", "trigger_event": "submission.graded",
        "action_type": "webhook", "action_config": {"url": "https://lms.test/sync"},
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["enabled"] is True

@pytest.mark.asyncio
async def test_create_notification_rule(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules", json={
        "name": "Alert", "trigger_event": "evaluation.failed",
        "action_type": "notification", "action_config": {"message": "Failed!"},
        "max_executions_per_hour": 5,
    }, headers=h)
    assert r.json()["data"]["max_executions_per_hour"] == 5

@pytest.mark.asyncio
async def test_list_and_delete_rule(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules", json={
        "name": "Del", "trigger_event": "pack.published",
        "action_type": "api_call", "action_config": {"path": "/notify"},
    }, headers=h)
    rule_id = r.json()["data"]["id"]
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules", headers=h)
    assert len(r.json()["data"]) >= 1
    r = await c.delete(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/rules/{rule_id}", headers=h)
    assert r.status_code == 200
