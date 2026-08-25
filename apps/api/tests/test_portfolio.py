"""Portfolio and public page tests."""

import pytest

from app.models.portfolio import ItemVisibility, ProfileVisibility
from app.schemas.portfolio import RESERVED_USERNAMES, USERNAME_PATTERN

# ── Public endpoints (no auth needed) ────────────────────────


def test_public_profile_endpoint_exists():
    """Public portfolio endpoints are registered."""
    from app.api.v1.endpoints.portfolio import router

    paths = [r.path for r in router.routes]
    # /u/{username} is a Next.js page; the API has /u/{username}/items
    assert any("/u/{username}" in p for p in paths)


def test_portfolio_router_has_public_endpoints():
    """Portfolio router has public /u/ endpoints registered."""
    from app.api.v1.endpoints.portfolio import router

    paths = [r.path for r in router.routes]
    assert "/u/{username}/items" in paths
    assert "/u/{username}/items/{slug}" in paths


# ── Auth protection (portfolio management) ───────────────────


@pytest.mark.asyncio
async def test_get_profile_requires_auth(client):
    r = await client.get("/api/v1/portfolio/profile")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_update_profile_requires_auth(client):
    r = await client.put("/api/v1/portfolio/profile", json={"headline": "test"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_change_username_requires_auth(client):
    r = await client.put("/api/v1/portfolio/username", json={"username": "testuser"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_items_requires_auth(client):
    r = await client.get("/api/v1/portfolio/items")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_create_item_requires_auth(client):
    r = await client.post("/api/v1/portfolio/items", json={"title": "Test"})
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_delete_item_requires_auth(client):
    r = await client.delete("/api/v1/portfolio/items/fake-id")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_list_badges_requires_auth(client):
    r = await client.get("/api/v1/portfolio/badges")
    assert r.status_code == 401


@pytest.mark.asyncio
async def test_toggle_badge_requires_auth(client):
    r = await client.put("/api/v1/portfolio/badges/fake", json={"show_on_profile": False})
    assert r.status_code == 401


# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_username_reserved_rejected(client):
    r = await client.put("/api/v1/portfolio/username", json={"username": "admin"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_username_too_short_rejected(client):
    r = await client.put("/api/v1/portfolio/username", json={"username": "ab"})
    assert r.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_item_title_too_short(client):
    r = await client.post("/api/v1/portfolio/items", json={"title": "A"})
    assert r.status_code in (401, 422)


# ── Null-clear on profile update ─────────────────────────────


@pytest.mark.asyncio
async def test_profile_null_clears_nullable_fields(client):
    """An explicit null for headline/bio/location/website_url must CLEAR the
    field; an empty body leaves everything unchanged. Regression for
    exclude_none / `if v is not None` dropping explicit nulls."""
    import uuid as _uuid

    from app.core.database import engine

    # Fresh pool: earlier tests may leave pooled connections bound to their
    # own (closed) event loops (same hygiene as test_auth.py)
    await engine.dispose()

    email = f"pf-{_uuid.uuid4().hex[:8]}@test.com"
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "TestPass123!", "display_name": "Pf User"},
    )
    assert r.status_code == 201
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}

    # Set the nullable fields
    r = await client.put(
        "/api/v1/portfolio/profile",
        json={
            "headline": "AI Creator",
            "bio": "original bio text",
            "location": "Shanghai",
            "website_url": "https://example.com",
        },
        headers=h,
    )
    assert r.status_code == 200
    assert r.json()["data"]["bio"] == "original bio text"

    # Empty body → all unchanged
    r = await client.put("/api/v1/portfolio/profile", json={}, headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["headline"] == "AI Creator"
    assert d["bio"] == "original bio text"
    assert d["location"] == "Shanghai"
    assert d["website_url"] == "https://example.com"

    # Explicit nulls → cleared
    r = await client.put(
        "/api/v1/portfolio/profile",
        json={"headline": None, "bio": None, "location": None, "website_url": None},
        headers=h,
    )
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["headline"] is None
    assert d["bio"] is None
    assert d["location"] is None
    assert d["website_url"] is None

    # Partial null: clear only bio, headline untouched
    r = await client.put(
        "/api/v1/portfolio/profile", json={"headline": "Back again"}, headers=h
    )
    assert r.status_code == 200
    r = await client.put("/api/v1/portfolio/profile", json={"bio": None}, headers=h)
    assert r.status_code == 200
    d = r.json()["data"]
    assert d["headline"] == "Back again"
    assert d["bio"] is None

    await engine.dispose()


# ── Unit tests ───────────────────────────────────────────────


def test_reserved_usernames():
    assert "admin" in RESERVED_USERNAMES
    assert "api" in RESERVED_USERNAMES
    assert "dashboard" in RESERVED_USERNAMES
    assert "login" in RESERVED_USERNAMES
    assert "register" in RESERVED_USERNAMES
    assert "notreserved" not in RESERVED_USERNAMES


def test_username_pattern_valid():
    assert USERNAME_PATTERN.match("alice")
    assert USERNAME_PATTERN.match("alice-wang")
    assert USERNAME_PATTERN.match("user123")
    assert USERNAME_PATTERN.match("a1b2c3d4")


def test_username_pattern_invalid():
    assert not USERNAME_PATTERN.match("ab")  # too short
    assert not USERNAME_PATTERN.match("Alice")  # uppercase
    assert not USERNAME_PATTERN.match("-alice")  # starts with hyphen
    assert not USERNAME_PATTERN.match("alice-")  # ends with hyphen
    assert not USERNAME_PATTERN.match("alice--bob")  # double hyphen


def test_profile_visibility_values():
    assert ProfileVisibility.PUBLIC.value == "public"
    assert ProfileVisibility.PRIVATE.value == "private"


def test_item_visibility_values():
    assert ItemVisibility.PUBLIC.value == "public"
    assert ItemVisibility.UNLISTED.value == "unlisted"
    assert ItemVisibility.PRIVATE.value == "private"


def test_slug_generation():
    from app.services.portfolio import PortfolioService

    assert PortfolioService._generate_slug("AI Chatbot v2") == "ai-chatbot-v2"
    assert len(PortfolioService._generate_slug("AB")) >= 3
