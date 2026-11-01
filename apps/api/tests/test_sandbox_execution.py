"""Tests for sandbox execution endpoint and service."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"sbx-{uuid.uuid4().hex[:8]}@test.com"


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


async def _setup_install(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Sbx"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"sbx-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Sbx Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    app_slug = f"sbxapp-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/apps",
        json={"name": "Sbx App", "slug": app_slug, "category": "automation"},
        headers=h,
    )
    app_id = r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/developer/apps/{app_id}/versions",
        json={
            "version": "1.0.0",
            "manifest": {"schema_version": "1.0", "app": {}, "permissions": []},
            "content_hash": "a" * 64,
        },
        headers=h,
    )
    v_id = r.json()["data"]["id"]
    org_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org_id = org_r.json()["data"]["id"]
    ir = await c.post(
        f"/api/v1/orgs/{org_id}/apps/install",
        json={"app_id": app_id, "app_version_id": v_id},
        headers=h,
    )
    inst_id = ir.json()["data"]["id"]
    return h, app_id, v_id, org_id, inst_id


@pytest.mark.asyncio
async def test_execute_function(c):
    """Execute a function in the sandbox."""
    h, app_id, v_id, org_id, inst_id = await _setup_install(c)
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute",
        json={
            "function_name": "on_submission_completed",
            "payload": {"submission_id": "test-123"},
            "timeout_seconds": 10,
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["success"] is True
    assert data["duration_ms"] >= 0
    assert data["output"] is not None


@pytest.mark.asyncio
async def test_execute_records_log(c):
    """Execution should be recorded in the log."""
    h, app_id, v_id, org_id, inst_id = await _setup_install(c)
    await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute",
        json={"function_name": "test_func", "payload": {}},
        headers=h,
    )
    # Check execution log
    r = await c.get(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/executions",
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 1


@pytest.mark.asyncio
async def test_execute_requires_org_admin(c):
    """Non-admin can't execute."""
    h1, _, _, org_id, inst_id = await _setup_install(c)
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Other"},
    )
    h2 = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = await c.post(
        f"/api/v1/orgs/{org_id}/apps/installations/{inst_id}/execute",
        json={"function_name": "test", "payload": {}},
        headers=h2,
    )
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_execute_wrong_org(c):
    """Can't execute on installation from different org."""
    h, _, _, org_id, inst_id = await _setup_install(c)
    org2_r = await c.post("/api/v1/orgs", json={"name": f"T-{uuid.uuid4().hex[:6]}"}, headers=h)
    org2_id = org2_r.json()["data"]["id"]
    r = await c.post(
        f"/api/v1/orgs/{org2_id}/apps/installations/{inst_id}/execute",
        json={"function_name": "test", "payload": {}},
        headers=h,
    )
    assert r.status_code == 404


# ── Sandbox service unit tests ───────────────────────────


def test_sandbox_result_defaults():
    from app.services.sandbox import SandboxResult

    r = SandboxResult(success=False)
    assert r.success is False
    assert r.output is None
    assert r.logs == []
    assert r.duration_ms == 0
    assert r.error is None


def test_sandbox_constants():
    from app.services.sandbox import (
        DEFAULT_MEMORY_MB,
        DEFAULT_TIMEOUT_SECONDS,
        MAX_MEMORY_MB,
        MAX_OUTPUT_BYTES,
        MAX_TIMEOUT_SECONDS,
    )

    assert DEFAULT_TIMEOUT_SECONDS == 30
    assert MAX_TIMEOUT_SECONDS == 300
    assert DEFAULT_MEMORY_MB == 128
    assert MAX_MEMORY_MB == 512
    assert MAX_OUTPUT_BYTES == 1_000_000
