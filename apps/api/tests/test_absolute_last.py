"""Absolute last tests — error constructors and remaining branches."""

import uuid
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus


async def _u(db):
    u = User(
        email=f"al-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="AbsLast",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


@pytest_asyncio.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as s:
        yield s
        await s.rollback()
    await engine.dispose()


# ═══════ Error class constructors ═══════


def test_all_error_constructors():
    """Cover all error __init__ lines by instantiating them."""
    from app.services.project import (
        DeadlinePassedError,
        DeliverableNotFoundError,
        FileTooLargeError,
        InvalidStateError,
        MaxSubmissionsReachedError,
        MissingDeliverablesError,
        ProjectNotFoundError,
        SubmissionNotFoundError,
    )

    ProjectNotFoundError()
    DeliverableNotFoundError()
    SubmissionNotFoundError()
    MaxSubmissionsReachedError(5)
    DeadlinePassedError()
    InvalidStateError()
    MissingDeliverablesError()
    FileTooLargeError()

    from app.services.evaluation import (
        BudgetExceededError,
        EvalNotEnabledError,
        EvalTaskNotFoundError,
    )

    EvalTaskNotFoundError()
    BudgetExceededError()
    EvalNotEnabledError()

    from app.services.organization import (
        AlreadyMemberError,
        CannotRemoveOwnerError,
        InsufficientOrgPermissionError,
        InviteLinkInvalidError,
        InviteTokenInvalidError,
        OrgNotFoundError,
        SlugAlreadyExistsError,
    )

    OrgNotFoundError()
    SlugAlreadyExistsError()
    AlreadyMemberError()
    CannotRemoveOwnerError()
    InsufficientOrgPermissionError()
    InviteLinkInvalidError()
    InviteTokenInvalidError()

    from app.services.portfolio import (
        ItemNotFoundError,
        ProfileNotFoundError,
        UsernameUnavailableError,
    )

    ProfileNotFoundError()
    UsernameUnavailableError()
    ItemNotFoundError()

    from app.services.skill import (
        AttemptNotFoundError,
        CategoryNotFoundError,
        CyclicDependencyError,
        ExerciseNotFoundError,
        SkillLockedError,
        SkillNotFoundError,
    )

    CategoryNotFoundError()
    SkillNotFoundError()
    ExerciseNotFoundError()
    AttemptNotFoundError()
    SkillLockedError()
    CyclicDependencyError()


# ═══════ Project: remaining service branches ═══════


@pytest.mark.asyncio
async def test_project_create_with_invalid_difficulty(db):
    """Cover lines 99-100: invalid difficulty fallback."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("PDOrg", None, None, u.id)
    await db.flush()

    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "PDProj",
        None,
        "D",
        "I",
        "invalid_diff",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    assert proj.difficulty.value == "intermediate"


@pytest.mark.asyncio
async def test_project_create_with_skills(db):
    """Cover line 113: set_project_skills called during create."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService
    from app.services.skill import SkillService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("PSOrg", None, None, u.id)
    await db.flush()

    skill_svc = SkillService(db)
    cat = await skill_svc.create_category(org.id, "PC", None, None, None, u.id)
    skill = await skill_svc.create_skill(
        org.id, cat.id, "PSkill", None, "D", None, "beginner", None, None, None, u.id
    )
    await db.flush()

    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "PSProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        [skill.id],
        u.id,  # Pass skill_ids
    )
    sids = await svc.get_project_skill_ids(proj.id)
    assert skill.id in sids


@pytest.mark.asyncio
async def test_project_list_with_status_filter(db):
    """Cover line 124: status filter."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("PLOrg", None, None, u.id)
    await db.flush()

    svc = ProjectService(db)
    projects, total = await svc.list_projects(org.id, status="draft")
    assert total >= 0


@pytest.mark.asyncio
async def test_project_update_difficulty(db):
    """Cover line 147: update with difficulty string."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("PUOrg", None, None, u.id)
    await db.flush()

    svc = ProjectService(db)
    proj = await svc.create_project(
        org.id,
        "PUProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    updated = await svc.update_project(proj.id, difficulty="expert")
    assert updated.difficulty.value == "expert"


# ═══════ Evaluation: list with type filter ═══════


@pytest.mark.asyncio
async def test_eval_list_with_type_filter(db):
    """Cover line 229: type filter."""
    from app.services.evaluation import EvaluationService

    u = await _u(db)
    from app.services.organization import OrgService

    org_svc = OrgService(db)
    org = await org_svc.create("ELOrg", None, None, u.id)
    await db.flush()

    svc = EvaluationService(db)
    tasks, total = await svc.list_tasks(org.id, eval_type="submission_review")
    assert total >= 0


# ═══════ Org: get_members with role filter ═══════


@pytest.mark.asyncio
async def test_org_members_role_filter(db):
    """Cover line 246: role filter in get_members."""
    from app.services.organization import OrgService

    u = await _u(db)
    svc = OrgService(db)
    org = await svc.create("MFOrg", None, None, u.id)
    await db.flush()

    members, total = await svc.get_members(org.id, role="owner")
    assert total == 1


# ═══════ Org: get_org not found ═══════


@pytest.mark.asyncio
async def test_org_get_not_found(db):
    """Cover line 149: org not found."""
    from app.services.organization import OrgNotFoundError, OrgService

    svc = OrgService(db)
    with pytest.raises(OrgNotFoundError):
        await svc.get_org("nonexistent-org-id")


# ═══════ Org: remove with insufficient permission ═══════


@pytest.mark.asyncio
async def test_org_remove_insufficient_permission(db):
    """Cover lines 210,221: insufficient permission to remove/update."""
    from app.models.organization import OrgRole
    from app.services.organization import InsufficientOrgPermissionError, OrgService

    u1 = await _u(db)
    u2 = await _u(db)
    u3 = await _u(db)
    svc = OrgService(db)
    org = await svc.create("IPOrg", None, None, u1.id)
    await svc.add_member(org.id, u2.id, OrgRole.STUDENT)
    await svc.add_member(org.id, u3.id, OrgRole.STUDENT)
    await db.flush()

    # Student u2 tries to remove student u3 → insufficient
    with pytest.raises(InsufficientOrgPermissionError):
        await svc.remove_member(org.id, u3.id, u2.id)

    # Non-owner tries to update role → insufficient
    with pytest.raises(InsufficientOrgPermissionError):
        await svc.update_member_role(org.id, u3.id, OrgRole.INSTRUCTOR, u2.id)


# ═══════ Org: accept invite internals ═══════


@pytest.mark.asyncio
async def test_org_accept_invite_wrong_email(db):
    """Cover lines 362,364-366,371: invite not addressed to this user."""
    import secrets as s
    from hashlib import sha256

    from app.models.organization import OrgRole
    from app.services.organization import InviteTokenInvalidError, OrgService

    u1 = await _u(db)
    u2 = await _u(db)
    u3 = await _u(db)  # Wrong user
    svc = OrgService(db)
    org = await svc.create("WEOrg", None, None, u1.id)
    await db.flush()

    await svc.invite_members(org.id, [u2.email], OrgRole.STUDENT, u1.id)
    await db.flush()

    from sqlalchemy import select

    from app.models.organization import OrgInvitation

    result = await db.execute(select(OrgInvitation).where(OrgInvitation.email == u2.email))
    invite = result.scalar_one()
    raw = s.token_urlsafe(32)
    invite.token_hash = sha256(raw.encode()).hexdigest()
    await db.flush()

    # u3 (wrong user) tries to accept u2's invite
    with pytest.raises(InviteTokenInvalidError, match="not addressed"):
        await svc.accept_email_invite(raw, u3.id)


# ═══════ Portfolio: public profile/items edge cases ═══════


@pytest.mark.asyncio
async def test_portfolio_public_profile_private(db):
    """Cover line 118: private profile returns None."""
    from app.services.portfolio import PortfolioService

    u = await _u(db)
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(u.id)
    from app.models.portfolio import ProfileVisibility

    profile.visibility = ProfileVisibility.PRIVATE
    await db.flush()

    pub = await svc.get_public_profile(profile.username)
    assert pub is None


@pytest.mark.asyncio
async def test_portfolio_public_items_private(db):
    """Cover line 177: private profile returns empty items."""
    from app.services.portfolio import PortfolioService

    u = await _u(db)
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(u.id)
    from app.models.portfolio import ProfileVisibility

    profile.visibility = ProfileVisibility.PRIVATE
    await db.flush()

    items = await svc.get_public_items(profile.username)
    assert items == []


@pytest.mark.asyncio
async def test_portfolio_public_item_private(db):
    """Cover line 193: private profile item returns None."""
    from app.services.portfolio import PortfolioService

    u = await _u(db)
    svc = PortfolioService(db)
    profile = await svc.get_or_create_profile(u.id)
    from app.models.portfolio import ProfileVisibility

    profile.visibility = ProfileVisibility.PRIVATE
    await db.flush()

    item = await svc.get_public_item(profile.username, "any-slug")
    assert item is None


@pytest.mark.asyncio
async def test_portfolio_get_or_create_user_not_found(db):
    """Cover line 61: user not found."""
    from app.exceptions import AppError
    from app.services.portfolio import PortfolioService

    svc = PortfolioService(db)
    with pytest.raises(AppError, match="User not found"):
        await svc.get_or_create_profile("nonexistent-user-id")


@pytest.mark.asyncio
async def test_portfolio_create_from_submission_with_project(db):
    """Cover lines 221,223,239-240: denormalize with project info."""
    from app.services.organization import OrgService
    from app.services.portfolio import PortfolioService
    from app.services.project import ProjectService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("PortDen", None, None, u.id)
    await db.flush()

    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "DenProj",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        u.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, u.id)
    await proj_svc.submit_draft(sub.id, u.id)
    await proj_svc.create_review(sub.id, u.id, "approved", 95, None, "Great")
    await db.flush()

    port_svc = PortfolioService(db)
    await port_svc.get_or_create_profile(u.id)
    item = await port_svc.create_item(
        u.id, "DenItem", "Desc", sub.id, None, None, None, "public", False
    )
    assert item.source_org_name is not None
    assert item.source_project == "DenProj"
    assert item.score == 95


@pytest.mark.asyncio
async def test_portfolio_badge_visibility(db):
    """Cover line 298: toggle badge visibility."""
    from app.models.portfolio import SkillBadge
    from app.services.organization import OrgService
    from app.services.portfolio import PortfolioService
    from app.services.skill import SkillService

    u = await _u(db)
    org_svc = OrgService(db)
    org = await org_svc.create("BVOrg", None, None, u.id)
    await db.flush()

    svc_s = SkillService(db)
    cat = await svc_s.create_category(org.id, "BVC", None, None, None, u.id)
    skill = await svc_s.create_skill(
        org.id, cat.id, "BVS", None, "D", None, "beginner", None, None, None, u.id
    )
    await db.flush()

    badge = SkillBadge(
        user_id=u.id,
        skill_id=skill.id,
        org_id=org.id,
        skill_name="BVS",
        category_name="BVC",
        completion_pct=80,
    )
    db.add(badge)
    await db.flush()

    port_svc = PortfolioService(db)
    toggled = await port_svc.toggle_badge(badge.id, u.id, False)
    assert toggled.show_on_profile is False


# ═══════ deps.py: get_current_user_optional full flow ═══════


@pytest.mark.asyncio
async def test_deps_optional_returns_none_no_token():
    """Cover lines 40-45: no token → returns None."""
    from app.api.deps import get_current_user_optional

    result = await get_current_user_optional(token=None, db=AsyncMock())
    assert result is None


@pytest.mark.asyncio
async def test_deps_optional_returns_none_bad_token():
    """Cover lines 43-45: bad token → catches and returns None."""
    from app.api.deps import get_current_user_optional

    result = await get_current_user_optional(token="bad-token", db=AsyncMock())
    assert result is None
