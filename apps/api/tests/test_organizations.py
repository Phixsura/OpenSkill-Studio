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
    assert not service._can_manage_member(
        make_member(OrgRole.INSTRUCTOR), make_member(OrgRole.ADMIN)
    )

    # Student cannot manage anyone
    assert not service._can_manage_member(
        make_member(OrgRole.STUDENT), make_member(OrgRole.STUDENT)
    )
    assert not service._can_manage_member(
        make_member(OrgRole.STUDENT), make_member(OrgRole.INSTRUCTOR)
    )


def test_slug_generation():
    """Test slug auto-generation from org name."""
    from app.services.organization import OrgService

    assert OrgService._generate_slug("AI 创作者训练营") is not None
    slug = OrgService._generate_slug("Phixsura Academy")
    assert slug == "phixsura-academy"
    assert len(OrgService._generate_slug("AB")) >= 3  # Short names get suffix


@pytest.mark.asyncio
async def test_org_member_matrix_and_seat_quota_r402():
    """R402 (org core was 4/45): the role/seat security matrix —
    (1) seat quota counts DISTINCT users per seat CLASS tenant-wide; a user
        already holding a same-class seat in a sibling org adds for FREE
        (R74[1]) while a genuinely new user at the cap is rejected;
    (2) the add-then-promote bypass is closed: promoting a student past the
        staff cap is rejected (issue #27 §2.5);
    (3) owners cannot be removed; a non-manager cannot remove a peer; the
        LAST owner cannot be demoted (400) while a second owner makes the
        demotion legal;
    (4) an unknown user id on add is a 404 (never an FK 500)."""
    from sqlalchemy import select as _sel
    from ulid import ULID as _ULID

    from app.controlplane.services.audit import Actor as _Actor
    from app.controlplane.services.entitlements import invalidate_cache
    from app.controlplane.services.plans import set_override
    from app.core.database import AsyncSessionLocal, engine
    from app.exceptions import AppError
    from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole
    from app.models.user import User
    from app.services.organization import (
        CannotRemoveOwnerError,
        InsufficientOrgPermissionError,
        OrgService,
    )
    _session_cm = AsyncSessionLocal()
    db = await _session_cm.__aenter__()
    try:

        async def _user(tag):
            u = User(email=f"{tag}-{str(_ULID()).lower()[:8]}@x.com",
                     display_name=tag, password_hash="x")
            db.add(u)
            await db.flush()
            return u

        owner = await _user("owner")
        svc = OrgService(db)
        org = await svc.create(name=f"R402 {_ULID()}", slug=f"r402-{str(_ULID()).lower()}",
                               description=None, created_by=owner.id)
        org2 = await svc.create(name=f"R402b {_ULID()}", slug=f"r402b-{str(_ULID()).lower()}",
                                description=None, created_by=owner.id)
        # same tenant for both orgs
        o2 = await db.get(Organization, org2.id)
        o2.tenant_id = org.tenant_id
        await db.flush()
        actor = _Actor(user_id=owner.id, type="platform")
        await set_override(db, org.tenant_id, "max_active_learners", value=2,
                           enforcement="hard", expires_at=None, reason="r402", actor=actor)
        await set_override(db, org.tenant_id, "max_instructors", value=2,
                           enforcement="hard", expires_at=None, reason="r402", actor=actor)
        await invalidate_cache(org.tenant_id)

        # (4) unknown user id → 404
        with pytest.raises(AppError) as e404:
            await svc.add_member(org.id, str(_ULID()), OrgRole.STUDENT)
        assert e404.value.status_code == 404

        # (1) two students fill the learner cap
        s1, s2 = await _user("s1"), await _user("s2")
        await svc.add_member(org.id, s1.id, OrgRole.STUDENT)
        await svc.add_member(org.id, s2.id, OrgRole.STUDENT)
        s3 = await _user("s3")
        with pytest.raises(Exception) as e_cap:
            await svc.add_member(org.id, s3.id, OrgRole.STUDENT)
        assert "quota" in str(e_cap.value).lower() or "limit" in str(e_cap.value).lower()
        # …but s1 joining the SIBLING org is FREE (already counted, R74[1])
        m_sib = await svc.add_member(org2.id, s1.id, OrgRole.STUDENT)
        assert m_sib.status == MemberStatus.ACTIVE

        # (2) staff cap: owner occupies 1 of 2; an instructor fills it; promoting
        # a student past the staff cap is rejected (add-then-promote closed)
        i1 = await _user("i1")
        await svc.add_member(org.id, i1.id, OrgRole.INSTRUCTOR)
        with pytest.raises(Exception) as e_promote:
            await svc.update_member_role(org.id, s2.id, OrgRole.INSTRUCTOR, owner.id)
        assert "quota" in str(e_promote.value).lower() or "limit" in str(e_promote.value).lower()

        # (3) governance: owner unremovable; instructor cannot remove a student
        # they don't manage? (peer-manage matrix) — and only an OWNER changes roles
        with pytest.raises(CannotRemoveOwnerError):
            await svc.remove_member(org.id, owner.id, owner.id)
        with pytest.raises(InsufficientOrgPermissionError):
            await svc.update_member_role(org.id, s1.id, OrgRole.STUDENT, i1.id)
        # a student cannot remove another student
        with pytest.raises(InsufficientOrgPermissionError):
            await svc.remove_member(org.id, s2.id, s1.id)
        # self-removal is allowed (leave)
        await svc.remove_member(org.id, s2.id, s2.id)
        m_left = (await db.execute(
            _sel(OrgMember).where(OrgMember.org_id == org.id,
                                  OrgMember.user_id == s2.id))).scalar_one()
        assert m_left.status == MemberStatus.ARCHIVED

        # LAST owner cannot be demoted; with a second owner it becomes legal
        with pytest.raises(AppError) as e_last:
            await svc.update_member_role(org.id, owner.id, OrgRole.ADMIN, owner.id)
        assert e_last.value.status_code == 400
        # (seat note: owner2 already holds a staff seat via org? no — new user;
        # staff cap is 2 with owner+i1 → bump the cap first)
        await set_override(db, org.tenant_id, "max_instructors", value=3,
                           enforcement="hard", expires_at=None, reason="r402b", actor=actor)
        await invalidate_cache(org.tenant_id)
        owner2 = await _user("owner2")
        await svc.add_member(org.id, owner2.id, OrgRole.OWNER)
        demoted = await svc.update_member_role(org.id, owner.id, OrgRole.ADMIN, owner.id)
        assert demoted.role == OrgRole.ADMIN

        # duplicate ACTIVE add → AlreadyMember; ARCHIVED re-add re-activates
        # THROUGH the quota gate (s2 left earlier; learner cap is 2 with s1 +
        # sibling s1 distinct-counted once → re-adding s2 fits)
        from app.services.organization import AlreadyMemberError

        with pytest.raises(AlreadyMemberError):
            await svc.add_member(org.id, s1.id, OrgRole.STUDENT)
        m_back = await svc.add_member(org.id, s2.id, OrgRole.STUDENT)
        assert m_back.status == MemberStatus.ACTIVE
        # …and at the cap a NEW student is still rejected (reactivation used
        # the same funnel — pin the funnel by hitting the cap right after)
        with pytest.raises(Exception) as e_cap2:
            await svc.add_member(org.id, s3.id, OrgRole.STUDENT)
        assert "quota" in str(e_cap2.value).lower() or "limit" in str(e_cap2.value).lower()

        # staff → student direction also consumes a LEARNER seat: cap is now
        # full (s1+s2), so demoting the instructor to student is rejected
        with pytest.raises(Exception) as e_demote:
            await svc.update_member_role(org.id, i1.id, OrgRole.STUDENT, owner2.id)
        assert "quota" in str(e_demote.value).lower() or "limit" in str(e_demote.value).lower()

        # cross-TENANT seats are invisible here: sx holds an ACTIVE student
        # seat in a DIFFERENT tenant's org — that must NOT read as
        # "already counted" (the join is Organization.id == member.org_id
        # scoped to THIS tenant), so at our full learner cap sx is rejected
        owner3, sx = await _user("owner3"), await _user("sx")
        org3 = await svc.create(name=f"R402c {_ULID()}",
                                slug=f"r402c-{str(_ULID()).lower()}",
                                description=None, created_by=owner3.id)
        assert (await db.get(Organization, org3.id)).tenant_id != org.tenant_id
        await svc.add_member(org3.id, sx.id, OrgRole.STUDENT)
        with pytest.raises(Exception) as e_xt:
            await svc.add_member(org.id, sx.id, OrgRole.STUDENT)
        assert "quota" in str(e_xt.value).lower() or "limit" in str(e_xt.value).lower()

        # LATERAL staff→staff moves consume no seat of ANY class: with staff
        # OVER a lowered cap (3 active vs cap 2) and learners AT cap, an
        # instructor→admin change must still succeed (neither the staff-quota
        # branch nor the student-quota branch may fire on staff→staff)…
        await set_override(db, org.tenant_id, "max_instructors", value=2,
                           enforcement="hard", expires_at=None, reason="r402c", actor=actor)
        await invalidate_cache(org.tenant_id)
        lat = await svc.update_member_role(org.id, i1.id, OrgRole.ADMIN, owner2.id)
        assert lat.role == OrgRole.ADMIN
        # …and with exactly ONE active owner (owner2), a non-owner→non-owner
        # change must not trip the LAST_OWNER guard (it only guards
        # owner→non-owner demotions)
        lat2 = await svc.update_member_role(org.id, owner.id, OrgRole.INSTRUCTOR, owner2.id)
        assert lat2.role == OrgRole.INSTRUCTOR

        # cohort cascade on removal: s2 in a cohort of THIS org and one of a
        # DIFFERENT org — removal deletes only this org's cohort membership
        from app.models.cohort import Cohort, CohortMember

        c_in = Cohort(org_id=org.id, name="In", slug=f"in-{str(_ULID()).lower()}",
                      created_by=owner2.id)
        c_out = Cohort(org_id=org2.id, name="Out", slug=f"out-{str(_ULID()).lower()}",
                       created_by=owner2.id)
        db.add_all([c_in, c_out])
        await db.flush()
        db.add_all([
            CohortMember(cohort_id=c_in.id, user_id=s2.id, role="learner"),
            CohortMember(cohort_id=c_out.id, user_id=s2.id, role="learner"),
        ])
        await db.flush()
        await svc.remove_member(org.id, s2.id, owner2.id)
        remaining = (await db.execute(
            _sel(CohortMember).where(CohortMember.user_id == s2.id))
        ).scalars().all()
        assert [cm.cohort_id for cm in remaining] == [c_out.id], (
            "removal cascades ONLY this org's cohort memberships")

        # delete_org: only an OWNER; archives member rows (freeing seats) and
        # the org's packs
        with pytest.raises(InsufficientOrgPermissionError):
            await svc.delete_org(org2.id, s1.id)     # s1 is a student there
        # delete_org archives the org's packs in BOTH registries — and ONLY
        # that org's (a sibling org's packs must not be collateral)
        from app.models.skill_pack import PackStatus, SkillPack
        from app.models.workflow_pack import WorkflowPack

        sp2 = SkillPack(owner_org_id=org2.id, name="P2",
                        slug=f"p2-{str(_ULID()).lower()}", created_by=owner.id)
        wf2 = WorkflowPack(owner_org_id=org2.id, name="W2",
                           slug=f"w2-{str(_ULID()).lower()}", created_by=owner.id)
        sp1 = SkillPack(owner_org_id=org.id, name="P1",
                        slug=f"p1-{str(_ULID()).lower()}", created_by=owner.id)
        db.add_all([sp2, wf2, sp1])
        await db.flush()
        await svc.delete_org(org2.id, owner.id)
        o2_after = await db.get(Organization, org2.id)
        assert o2_after.status.value == "archived"
        sib_row = (await db.execute(
            _sel(OrgMember).where(OrgMember.org_id == org2.id,
                                  OrgMember.user_id == s1.id))).scalar_one()
        assert sib_row.status == MemberStatus.ARCHIVED
        await db.refresh(sp2)
        await db.refresh(wf2)
        await db.refresh(sp1)
        assert sp2.status == PackStatus.ARCHIVED, "org2's skill pack archived"
        assert str(wf2.status) in (str(PackStatus.ARCHIVED), "PackStatus.ARCHIVED", "archived") \
            or getattr(wf2.status, "value", wf2.status) == "archived"
        assert sp1.status != PackStatus.ARCHIVED, "sibling org's pack untouched"
    finally:
        await db.rollback()
        await _session_cm.__aexit__(None, None, None)
        await engine.dispose()
