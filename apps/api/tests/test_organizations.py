"""Organization endpoint + RBAC tests."""

import pytest

from app.models.organization import ROLE_HIERARCHY, OrgRole

# ── Schema validation ────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_org_missing_name(client):
    response = await client.post("/api/v1/orgs", json={})
    assert response.status_code in (401, 422)


@pytest.mark.asyncio
async def test_create_org_requires_auth(client):
    response = await client.post(
        "/api/v1/orgs",
        json={"name": "Test Org"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_orgs_requires_auth(client):
    response = await client.get("/api/v1/orgs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_org_requires_auth(client):
    response = await client.get("/api/v1/orgs/fake-id")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_org_requires_auth(client):
    response = await client.put("/api/v1/orgs/fake-id", json={"name": "New"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_org_requires_auth(client):
    response = await client.delete("/api/v1/orgs/fake-id")
    assert response.status_code == 401


# ── Members ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_list_members_requires_auth(client):
    response = await client.get("/api/v1/orgs/fake-id/members")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_member_role_requires_auth(client):
    response = await client.put(
        "/api/v1/orgs/fake-id/members/user-id",
        json={"role": "student"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_remove_member_requires_auth(client):
    response = await client.delete("/api/v1/orgs/fake-id/members/user-id")
    assert response.status_code == 401


# ── Invitations ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invite_members_requires_auth(client):
    response = await client.post(
        "/api/v1/orgs/fake-id/invites",
        json={"emails": ["test@example.com"], "role": "student"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invite_members_empty_emails_validation(client):
    """Even if auth worked, empty emails should be caught by Pydantic."""
    response = await client.post(
        "/api/v1/orgs/fake-id/invites",
        json={"emails": [], "role": "student"},
    )
    assert response.status_code in (401, 422)


# ── Invite Links ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_invite_link_requires_auth(client):
    response = await client.post(
        "/api/v1/orgs/fake-id/invite-links",
        json={"role": "student"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_join_by_code_requires_auth(client):
    response = await client.post(
        "/api/v1/invites/join",
        json={"code": "abc123"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_accept_invite_requires_auth(client):
    response = await client.post(
        "/api/v1/invites/accept",
        json={"token": "some-token"},
    )
    assert response.status_code == 401


# ── Settings ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_settings_requires_auth(client):
    response = await client.put(
        "/api/v1/orgs/fake-id/settings",
        json={"settings": {"max_members": 50}},
    )
    assert response.status_code == 401


# ── Role hierarchy unit tests ────────────────────────────────


def test_role_hierarchy_order():
    """Owner < Admin < Instructor < Student in privilege ordering."""
    assert ROLE_HIERARCHY[OrgRole.OWNER] < ROLE_HIERARCHY[OrgRole.ADMIN]
    assert ROLE_HIERARCHY[OrgRole.ADMIN] < ROLE_HIERARCHY[OrgRole.INSTRUCTOR]
    assert ROLE_HIERARCHY[OrgRole.INSTRUCTOR] < ROLE_HIERARCHY[OrgRole.STUDENT]


def test_can_manage_member_logic():
    """Test the role hierarchy management rules."""
    from unittest.mock import MagicMock

    from app.services.organization import OrgService

    # Mock service (no DB needed)
    service = OrgService.__new__(OrgService)

    def make_member(role: OrgRole):
        m = MagicMock()
        m.role = role
        return m

    # Owner can manage all below
    assert service._can_manage_member(make_member(OrgRole.OWNER), make_member(OrgRole.ADMIN))
    assert service._can_manage_member(make_member(OrgRole.OWNER), make_member(OrgRole.INSTRUCTOR))
    assert service._can_manage_member(make_member(OrgRole.OWNER), make_member(OrgRole.STUDENT))

    # Admin can manage instructor and student
    assert service._can_manage_member(make_member(OrgRole.ADMIN), make_member(OrgRole.INSTRUCTOR))
    assert service._can_manage_member(make_member(OrgRole.ADMIN), make_member(OrgRole.STUDENT))
    # Admin cannot manage owner or other admin
    assert not service._can_manage_member(make_member(OrgRole.ADMIN), make_member(OrgRole.OWNER))
    assert not service._can_manage_member(make_member(OrgRole.ADMIN), make_member(OrgRole.ADMIN))

    # Instructor can manage student only
    assert service._can_manage_member(make_member(OrgRole.INSTRUCTOR), make_member(OrgRole.STUDENT))
    assert not service._can_manage_member(make_member(OrgRole.INSTRUCTOR), make_member(OrgRole.ADMIN))

    # Student cannot manage anyone
    assert not service._can_manage_member(make_member(OrgRole.STUDENT), make_member(OrgRole.STUDENT))
    assert not service._can_manage_member(make_member(OrgRole.STUDENT), make_member(OrgRole.INSTRUCTOR))


def test_slug_generation():
    """Test slug auto-generation from org name."""
    from app.services.organization import OrgService

    assert OrgService._generate_slug("AI 创作者训练营") is not None
    slug = OrgService._generate_slug("Phixsura Academy")
    assert slug == "phixsura-academy"
    assert len(OrgService._generate_slug("AB")) >= 3  # Short names get suffix
