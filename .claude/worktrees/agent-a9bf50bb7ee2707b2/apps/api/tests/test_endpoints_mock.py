"""Endpoint tests with mocked dependencies for handler body coverage."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import ASGITransport, AsyncClient


def make_mock_user():
    """Create a mock authenticated user."""
    from app.models.user import User, UserRole, UserStatus

    user = MagicMock(spec=User)
    user.id = "01TESTUSER"
    user.email = "test@example.com"
    user.display_name = "Test User"
    user.avatar_url = None
    user.email_verified = True
    user.role = UserRole.STUDENT
    user.status = UserStatus.ACTIVE
    user.is_active = True
    user.has_password = True
    user.created_at = MagicMock()
    user.updated_at = MagicMock()
    user.last_login_at = None
    return user


def make_mock_member(role="student"):
    """Create a mock org member."""
    from app.models.organization import MemberStatus, OrgRole

    member = MagicMock()
    member.role = OrgRole(role)
    member.status = MemberStatus.ACTIVE
    return member


@pytest.fixture
async def auth_client():
    """Client with mocked auth — all requests appear as authenticated user."""
    from app.api.deps import get_current_user, get_db
    from app.main import app

    mock_user = make_mock_user()
    mock_db = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()
    mock_db.add = MagicMock()

    app.dependency_overrides[get_current_user] = lambda: mock_user
    app.dependency_overrides[get_db] = lambda: mock_db

    # Patch lifespan
    original = app.router.lifespan_context
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def noop(app):
        yield

    app.router.lifespan_context = noop

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac, mock_user, mock_db

    app.dependency_overrides.clear()
    app.router.lifespan_context = original


# ── Health endpoints ─────────────────────────────────────────


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_liveness(self, client):
        r = await client.get("/api/v1/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ── Auth endpoints with auth ─────────────────────────────────


class TestAuthEndpointsAuthed:
    @pytest.mark.asyncio
    async def test_get_me(self, auth_client):
        client, user, db = auth_client
        r = await client.get("/api/v1/auth/me")
        assert r.status_code == 200
        data = r.json()
        assert data["data"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_update_me(self, auth_client):
        client, user, db = auth_client
        r = await client.put("/api/v1/auth/me", json={"display_name": "New Name"})
        assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_sessions_list(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.auth.AuthService.list_sessions", new_callable=AsyncMock, return_value=[]):
            r = await client.get("/api/v1/auth/sessions")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_resend_verification(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.auth.AuthService.resend_verification", new_callable=AsyncMock):
            r = await client.post("/api/v1/auth/resend-verification")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_logout_no_cookie(self, auth_client):
        client, user, db = auth_client
        r = await client.post("/api/v1/auth/logout")
        assert r.status_code == 204


# ── Admin endpoints ──────────────────────────────────────────


class TestAdminEndpoints:
    @pytest.mark.asyncio
    async def test_admin_list_users_forbidden_for_student(self, auth_client):
        client, user, db = auth_client
        r = await client.get("/api/v1/admin/users")
        assert r.status_code == 403  # Student can't access admin

    @pytest.mark.asyncio
    async def test_admin_get_user_forbidden(self, auth_client):
        client, user, db = auth_client
        r = await client.get("/api/v1/admin/users/some-id")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_delete_user_forbidden(self, auth_client):
        client, user, db = auth_client
        r = await client.delete("/api/v1/admin/users/some-id")
        assert r.status_code == 403

    @pytest.mark.asyncio
    async def test_admin_update_role_forbidden(self, auth_client):
        client, user, db = auth_client
        r = await client.put("/api/v1/admin/users/x/role", json={"role": "admin"})
        assert r.status_code == 403


# ── Portfolio endpoints (authed) ─────────────────────────────


class TestPortfolioEndpointsAuthed:
    @pytest.mark.asyncio
    async def test_get_profile(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.portfolio.PortfolioService.get_or_create_profile", new_callable=AsyncMock) as mock:
            profile = MagicMock()
            profile.user_id = user.id
            profile.username = "testuser"
            profile.headline = None
            profile.bio = None
            profile.location = None
            profile.website_url = None
            profile.social_links = {}
            profile.visibility = "public"
            profile.theme = "default"
            profile.created_at = MagicMock()
            mock.return_value = profile

            r = await client.get("/api/v1/portfolio/profile")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_list_items(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.portfolio.PortfolioService.list_items", new_callable=AsyncMock, return_value=[]):
            r = await client.get("/api/v1/portfolio/items")
            assert r.status_code == 200

    @pytest.mark.asyncio
    async def test_list_badges(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.portfolio.PortfolioService.list_badges", new_callable=AsyncMock, return_value=[]):
            r = await client.get("/api/v1/portfolio/badges")
            assert r.status_code == 200


# ── Org endpoints (need membership mock) ─────────────────────


class TestOrgEndpointsAuthed:
    @pytest.mark.asyncio
    async def test_create_org(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.organization.OrgService.create", new_callable=AsyncMock) as mock_create, \
             patch("app.services.organization.OrgService.get_member_count", new_callable=AsyncMock, return_value=1):
            org = MagicMock()
            org.id = "01ORG"
            org.name = "Test Org"
            org.slug = "test-org"
            org.description = None
            org.logo_url = None
            org.created_at = MagicMock()
            mock_create.return_value = org

            r = await client.post("/api/v1/orgs", json={"name": "Test Org"})
            assert r.status_code == 201

    @pytest.mark.asyncio
    async def test_list_orgs(self, auth_client):
        client, user, db = auth_client
        with patch("app.services.organization.OrgService.get_user_orgs", new_callable=AsyncMock, return_value=[]):
            r = await client.get("/api/v1/orgs")
            assert r.status_code == 200
