"""Thorough CRUD tests for developer accounts."""

import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient


def _email():
    return f"crud-{uuid.uuid4().hex[:8]}@test.com"


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


@pytest.mark.asyncio
async def test_create_account_full_fields(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "CRUD"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"crud-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={
            "display_name": "CRUD Developer",
            "slug": slug,
            "support_email": f"{slug}@example.com",
            "website_url": "https://crud-developer.example.com",
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["display_name"] == "CRUD Developer"
    assert data["slug"] == slug
    assert data["website_url"] == "https://crud-developer.example.com"
    assert data["status"] in ("ACTIVE", "active")
    assert data["verified"] is False


@pytest.mark.asyncio
async def test_update_all_fields(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Upd"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"upd-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Old Name", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    acct_id = r.json()["data"]["id"]

    r = await c.patch(
        f"/api/v1/developer/accounts/{acct_id}",
        json={
            "display_name": "New Name",
            "support_email": "new@example.com",
            "website_url": "https://new.example.com",
        },
        headers=h,
    )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["display_name"] == "New Name"
    assert data["support_email"] == "new@example.com"
    assert data["website_url"] == "https://new.example.com"


@pytest.mark.asyncio
async def test_get_account_by_id(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Get"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"get-{uuid.uuid4().hex[:6]}"
    r = await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Get Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )
    acct_id = r.json()["data"]["id"]

    r = await c.get(f"/api/v1/developer/accounts/{acct_id}", headers=h)
    assert r.status_code == 200
    assert r.json()["data"]["id"] == acct_id


@pytest.mark.asyncio
async def test_list_accounts_returns_multiple(c):
    # Create 2 accounts
    for _ in range(2):
        r = await c.post(
            "/api/v1/auth/register",
            json={"email": _email(), "password": "TestPass123!", "display_name": "List"},
        )
        h = {"Authorization": f"Bearer {r.json()['access_token']}"}
        slug = f"list-{uuid.uuid4().hex[:6]}"
        await c.post(
            "/api/v1/developer/accounts",
            json={"display_name": "List Dev", "slug": slug, "support_email": f"{slug}@t.com"},
            headers=h,
        )

    r = await c.get("/api/v1/developer/accounts", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["total"] >= 2


@pytest.mark.asyncio
async def test_list_accounts_pagination(c):
    r = await c.post(
        "/api/v1/auth/register",
        json={"email": _email(), "password": "TestPass123!", "display_name": "Page"},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    slug = f"pg-{uuid.uuid4().hex[:6]}"
    await c.post(
        "/api/v1/developer/accounts",
        json={"display_name": "Page Dev", "slug": slug, "support_email": f"{slug}@t.com"},
        headers=h,
    )

    r = await c.get("/api/v1/developer/accounts?page=1&per_page=1", headers=h)
    assert r.status_code == 200
    assert r.json()["meta"]["per_page"] == 1
