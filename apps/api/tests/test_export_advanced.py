"""Advanced export tests and additional endpoint coverage."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"adv-{uuid.uuid4().hex[:8]}@test.com"


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
        json={"email": _email(), "password": "TestPass123!", "display_name": "Adv"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"adv-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Adv Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    return h, slug


# ── OpenAPI spec ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_openapi_spec_endpoint(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/openapi.json", headers=h)
    assert r.status_code == 200
    spec = r.json()
    assert spec["info"]["title"] == "OpenSkill Developer Platform API"
    assert "paths" in spec
    # Should only include developer-facing paths
    for path in spec["paths"]:
        assert any(
            path.startswith(prefix)
            for prefix in ["/api/v1/developer/", "/api/v1/marketplace/", "/api/v1/oauth/", "/api/v1/orgs/"]
        ), f"Non-developer path in spec: {path}"


# ── Marketplace endpoints ────────────────────────────────


@pytest.mark.asyncio
async def test_marketplace_categories(c):
    r = await c.get("/api/v1/marketplace/categories")
    assert r.status_code == 200
    assert len(r.json()["data"]) == 7


@pytest.mark.asyncio
async def test_marketplace_featured(c):
    r = await c.get("/api/v1/marketplace/featured?limit=3")
    assert r.status_code == 200
    assert isinstance(r.json()["data"], list)


@pytest.mark.asyncio
async def test_marketplace_recent(c):
    r = await c.get("/api/v1/marketplace/recent?limit=5")
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_marketplace_trending(c):
    r = await c.get("/api/v1/marketplace/trending?days=7")
    assert r.status_code == 200


# ── Developer tools comprehensive ───────────────────────


@pytest.mark.asyncio
async def test_tools_event_types_complete(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/event-types", headers=h)
    data = r.json()["data"]
    assert data["total"] >= 35
    # Must have all main categories
    cats = set(data["categories"].keys())
    for expected in ["submission", "cohort", "project", "pack", "workflow", "talent", "marketplace", "app", "org", "evaluation"]:
        assert expected in cats, f"Missing category: {expected}"


@pytest.mark.asyncio
async def test_tools_permissions_complete(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/permissions", headers=h)
    data = r.json()["data"]
    assert data["total"] >= 30
    cats = set(data["categories"].keys())
    assert "read" in cats
    assert "write" in cats
    assert "subscribe" in cats
    assert "extend" in cats


@pytest.mark.asyncio
async def test_tools_ui_surfaces_complete(c):
    h, _ = await _setup(c)
    r = await c.get("/api/v1/developer/tools/ui-surfaces", headers=h)
    data = r.json()["data"]
    assert data["total"] == 8
    surface_ids = {s["id"] for s in data["surfaces"]}
    for expected in ["dashboard_card", "project_sidebar", "cohort_tool", "submission_panel", "registry_detail", "settings_page", "client_portal_widget", "operator_console"]:
        assert expected in surface_ids, f"Missing surface: {expected}"


@pytest.mark.asyncio
async def test_tools_fixtures_complete(c):
    h, _ = await _setup(c)
    r = await c.post("/api/v1/developer/tools/generate-fixtures", headers=h)
    data = r.json()["data"]
    assert "cohort" in data
    assert "project" in data
    assert "submission" in data
    assert "user" in data
    assert "organization" in data
    assert "event_payload" in data
    # Event payloads should include multiple event types
    assert "submission.completed" in data["event_payload"]
    assert "cohort.member_added" in data["event_payload"]
    assert "pack.published" in data["event_payload"]


# ── App listing filters ──────────────────────────────────


@pytest.mark.asyncio
async def test_list_apps_by_category(c):
    h, _ = await _setup(c)
    # Create apps in different categories
    for cat in ["connector", "analytics"]:
        slug = f"{cat[:4]}-{uuid.uuid4().hex[:4]}"
        await c.post(
            "/api/v1/developer/apps",
            json={"name": f"{cat} App", "slug": slug, "category": cat},
            headers=h,
        )
    r = await c.get("/api/v1/developer/apps?category=connector", headers=h)
    assert r.status_code == 200
    for app in r.json()["data"]:
        assert app["category"] in ("connector", "CONNECTOR")


@pytest.mark.asyncio
async def test_list_apps_pagination(c):
    h, _ = await _setup(c)
    # Create 3 apps
    for i in range(3):
        slug = f"pg-{uuid.uuid4().hex[:6]}"
        await c.post(
            "/api/v1/developer/apps",
            json={"name": f"Page App {i}", "slug": slug, "category": "connector"},
            headers=h,
        )
    r = await c.get("/api/v1/developer/apps?page=1&per_page=2", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) <= 2
    assert r.json()["meta"]["per_page"] == 2
