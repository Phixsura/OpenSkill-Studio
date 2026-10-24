"""Advanced developer apps CRUD and lifecycle tests."""

import uuid
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"daa-{uuid.uuid4().hex[:8]}@test.com"


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


async def _dev(c):
    r = await c.post("/api/v1/auth/register", json={"email": _email(), "password": "TestPass123!", "display_name": "DAA"})
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"daa-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/accounts", json={"display_name": "DAA Dev", "slug": slug, "support_email": f"{slug}@t.com"}, headers=h)
    return h


@pytest.mark.asyncio
async def test_create_all_categories(c):
    h = await _dev(c)
    cats = ["connector", "workflow-adapter", "ui-extension", "analytics", "automation", "content-pack", "ecosystem-source"]
    for cat_slug in cats:
        cat = cat_slug.replace("-", "_")
        s = f"{cat_slug[:6]}-{uuid.uuid4().hex[:4]}"
        r = await c.post("/api/v1/developer/apps", json={"name": f"{cat} App", "slug": s, "category": cat}, headers=h)
        assert r.status_code == 200, f"Failed for {cat}: {r.json()}"


@pytest.mark.asyncio
async def test_app_has_oauth_credentials(c):
    h = await _dev(c)
    s = f"oauth-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "OAuth App", "slug": s, "category": "connector"}, headers=h)
    data = r.json()["data"]
    assert data["oauth_client_id"].startswith("osk_")
    assert len(data["oauth_client_id"]) > 20


@pytest.mark.asyncio
async def test_get_app_detail(c):
    h = await _dev(c)
    s = f"det-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Detail App", "slug": s, "category": "analytics", "description": "Detailed"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.get(f"/api/v1/developer/apps/{app_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["description"] == "Detailed"


@pytest.mark.asyncio
async def test_update_webhook_url(c):
    h = await _dev(c)
    s = f"wh-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "WH App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.patch(f"/api/v1/developer/apps/{app_id}", json={"webhook_url": "https://hooks.example.com/openskill"}, headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["webhook_url"] == "https://hooks.example.com/openskill"


@pytest.mark.asyncio
async def test_app_list_with_developer_filter(c):
    h = await _dev(c)
    # Get dev account
    r = await c.get("/api/v1/developer/accounts/me", headers=h)
    dev_id = r.json()["data"]["id"]
    # Create app
    s = f"flt-{uuid.uuid4().hex[:6]}"
    await c.post("/api/v1/developer/apps", json={"name": "Filter App", "slug": s, "category": "connector"}, headers=h)
    # Filter by developer
    r = await c.get(f"/api/v1/developer/apps?developer_id={dev_id}", headers=h)
    assert r.status_code == 200
    assert len(r.json()["data"]) >= 1


@pytest.mark.asyncio
async def test_revoke_cleans_up(c):
    h = await _dev(c)
    s = f"rev-{uuid.uuid4().hex[:6]}"
    r = await c.post("/api/v1/developer/apps", json={"name": "Rev App", "slug": s, "category": "connector"}, headers=h)
    app_id = r.json()["data"]["id"]
    r = await c.post(f"/api/v1/developer/apps/{app_id}/revoke", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["status"] in ("revoked", "REVOKED")
