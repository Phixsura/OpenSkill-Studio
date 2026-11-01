"""Advanced sandbox execution tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"sbxa-{uuid.uuid4().hex[:8]}@test.com"

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
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "SbxA"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sbxa-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "SbxA Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    s = f"sbxaapp-{uuid.uuid4().hex[:4]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "SbxA App", "slug": s, "category": "automation"}, headers=h)
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
async def test_execute_returns_output(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "handler", "payload": {"key": "value"},
    }, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["success"] is True
    assert r.json()["data"]["output"] is not None

@pytest.mark.asyncio
async def test_execute_records_duration(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "fast_fn", "payload": {},
    }, headers=h)
    assert r.json()["data"]["duration_ms"] >= 0

@pytest.mark.asyncio
async def test_execute_appears_in_log(c):
    h, org_id, inst_id = await _installed(c)
    await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "logged_fn", "payload": {},
    }, headers=h)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/executions", headers=h)
    assert r.json()["meta"]["total"] >= 1

@pytest.mark.asyncio
async def test_execute_with_custom_timeout(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "timeout_fn", "payload": {}, "timeout_seconds": 5,
    }, headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_execute_with_memory(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "mem_fn", "payload": {}, "memory_mb": 64,
    }, headers=h)
    assert r.status_code == 200

@pytest.mark.asyncio
async def test_execute_wrong_org_rejected(c):
    h, org_id, inst_id = await _installed(c)
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:4]}"}, headers=h)
    org2 = org2_r.json()["data"]["id"]
    r = await c.post(f"/api/v1/orgs/{org2}/apps/installations/{inst_id}/execute", json={
        "function_name": "x", "payload": {},
    }, headers=h)
    assert r.status_code == 404

@pytest.mark.asyncio
async def test_execute_non_member_rejected(c):
    h, org_id, inst_id = await _installed(c)
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "Other"})
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
        "function_name": "x", "payload": {},
    }, headers=h2)
    assert r.status_code == 403

@pytest.mark.asyncio
async def test_execution_log_pagination(c):
    h, org_id, inst_id = await _installed(c)
    for i in range(3):
        await c.post(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute", json={
            "function_name": f"fn_{i}", "payload": {},
        }, headers=h)
    r = await c.get(f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/executions?page=1&per_page=2", headers=h)
    assert r.json()["meta"]["per_page"] == 2
    assert r.json()["meta"]["total"] >= 3
