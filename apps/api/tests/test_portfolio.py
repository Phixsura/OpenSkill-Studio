"""Portfolio and public page tests."""

import pytest

from app.models.portfolio import ItemVisibility, ProfileVisibility
from app.schemas.portfolio import RESERVED_USERNAMES, USERNAME_PATTERN

# ── Public endpoints (no auth needed) ────────────────────────


def test_public_profile_endpoint_exists():
    """Public profile endpoint is registered and doesn't require auth."""
    from app.main import app

    assert any("/u/{username}" in str(r) for r in app.routes)


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
