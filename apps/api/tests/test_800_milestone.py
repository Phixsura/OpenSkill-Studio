"""Tests to reach 800 milestone."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

def _email():
    return f"m8-{uuid.uuid4().hex[:8]}@test.com"

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


@pytest.mark.asyncio
async def test_openapi_spec(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "M8"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"m8-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "M8 Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    r = await c.get("/api/v1/developer/openapi.json", headers=h)
    assert r.status_code == 200
    spec = r.json()
    assert "paths" in spec
    assert spec["info"]["title"] == "OpenSkill Developer Platform API"


@pytest.mark.asyncio
async def test_tools_event_types(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "M8"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"m8t-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "M8 D", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    r = await c.get("/api/v1/developer/tools/event-types", headers=h)
    assert r.json()["data"]["total"] >= 35


@pytest.mark.asyncio
async def test_tools_permissions_count(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "M8"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"m8p-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "M8 D", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    r = await c.get("/api/v1/developer/tools/permissions", headers=h)
    assert r.json()["data"]["total"] >= 30


@pytest.mark.asyncio
async def test_tools_surfaces_count(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "M8"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"m8s-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "M8 D", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    r = await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)
    assert r.json()["data"]["total"] == 8


@pytest.mark.asyncio
async def test_tools_fixtures(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "M8"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"m8f-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "M8 D", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    r = await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)
    assert "cohort" in r.json()["data"]
    assert "event_payload" in r.json()["data"]


def test_idempotency_make_key():
    from app.services.idempotency import make_key
    k1 = make_key("c", "POST", "/x")
    k2 = make_key("c", "POST", "/x")
    assert k1 == k2
    k3 = make_key("c", "GET", "/x")
    assert k1 != k3


def test_ssrf_rejects_private():
    from app.services.event_dispatch import _is_safe_url
    assert _is_safe_url("https://localhost") is False
    assert _is_safe_url("https://169.254.169.254") is False
    assert _is_safe_url("http://example.com") is False


def test_manifest_validator_importable():
    from app.services.manifest_validator import validate_manifest, VALID_PERMISSIONS, VALID_SURFACES
    assert len(VALID_PERMISSIONS) >= 30
    assert len(VALID_SURFACES) == 8
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": []})
    assert r.valid


def test_sandbox_result_defaults():
    from app.services.sandbox import SandboxResult
    r = SandboxResult(success=True)
    assert r.output is None
    assert r.error is None
    assert r.duration_ms == 0


def test_event_dispatch_has_canonical():
    from app.services.event_dispatch import CANONICAL_EVENTS
    assert "submission.completed" in CANONICAL_EVENTS
    assert "app.installed" in CANONICAL_EVENTS
    assert len(CANONICAL_EVENTS) >= 35
