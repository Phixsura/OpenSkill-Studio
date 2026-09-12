"""R425: creator-assignment state machine — cross-org IDOR guards + re-offer.

offer/respond/withdraw are the paid-creator assignment lifecycle. The
org-scope guards are IDOR protections; the re-offer-in-place logic keeps a
declined creator revisitable without tripping the unique index.

Documented EQUIVALENT mutants (adjudicated): the 404->405 / 409->410 swaps
are HTTP status-class cosmetics (codes pinned, exact number is not).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, role=UserRole.ADMIN):
    u = User(
        email=f"r425-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R425",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R425 {uuid.uuid4().hex[:6]}",
        slug=f"r425-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def _member(db, org, role=UserRole.STUDENT):
    from app.services.organization import OrgService

    u = await _user(db, role)
    await OrgService(db).add_member(org.id, u.id, OrgRole.STUDENT)
    return u


async def _project(db, org, owner, *, published=True):
    from app.models.project import ContentStatus
    from app.services.project import ProjectService

    p = await ProjectService(db).create_project(
        org.id, f"P {uuid.uuid4().hex[:4]}", None, "d", "i", "beginner", 100,
        [], None, None, 0, 0, None, owner.id,
    )
    if published:
        p.status = ContentStatus.PUBLISHED
        await db.flush()
    return p


async def test_offer_cross_org_and_guards_r425(db):
    from app.models.project import ContentStatus
    from app.services.creator_matching import CreatorMatchingService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = CreatorMatchingService(db)
    creator = await _member(db, org)

    # a project in ANOTHER org → PROJECT_NOT_FOUND (kills the `is None or
    # wrong-org` -> `and` mutant: an `and` would let a cross-org project pass)
    foreign_proj = await _project(db, other_org, owner)
    with pytest.raises(AppError) as e_x:
        await svc.offer_assignment(org.id, foreign_proj.id, creator.id, owner.id)
    assert e_x.value.code == "PROJECT_NOT_FOUND"

    # archived project → offers closed (409)
    proj = await _project(db, org, owner)
    arch = await _project(db, org, owner)
    arch.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError) as e_arch:
        await svc.offer_assignment(org.id, arch.id, creator.id, owner.id)
    assert e_arch.value.code == "PROJECT_NOT_AVAILABLE"

    # a non-member creator → 422
    stranger = await _user(db, UserRole.STUDENT)
    with pytest.raises(AppError) as e_nm:
        await svc.offer_assignment(org.id, proj.id, stranger.id, owner.id)
    assert e_nm.value.code == "NOT_A_MEMBER"

    # a bogus match_run_id (loose ref) → 404
    with pytest.raises(AppError) as e_mr:
        await svc.offer_assignment(org.id, proj.id, creator.id, owner.id,
                                   match_run_id=str(uuid.uuid4()))
    assert e_mr.value.code == "MATCH_RUN_NOT_FOUND"


async def test_offer_reoffer_state_machine_r425(db):
    from app.services.creator_matching import CreatorMatchingService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = CreatorMatchingService(db)
    creator = await _member(db, org)
    proj = await _project(db, org, owner)

    # first offer
    a1 = await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)
    assert a1.status == "offered"
    # a second offer while still 'offered' → 409 (active conflict)
    with pytest.raises(AppError) as e_dup:
        await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)
    assert e_dup.value.code == "ASSIGNMENT_EXISTS"

    # creator declines → the SAME row can be re-offered in place (no unique
    # violation, no new row)
    declined = await svc.respond_assignment(a1.id, org.id, creator.id, accept=False)
    assert declined.status == "declined"
    a2 = await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)
    assert a2.id == a1.id  # reopened in place
    assert a2.status == "offered"
    assert a2.responded_at is None

    # accept → an offer against this creator+project is now an active conflict
    accepted = await svc.respond_assignment(a2.id, org.id, creator.id, accept=True)
    assert accepted.status == "accepted"
    with pytest.raises(AppError) as e_dup2:
        await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)
    assert e_dup2.value.code == "ASSIGNMENT_EXISTS"


async def test_respond_guards_cross_org_and_ownership_r425(db):
    from app.services.creator_matching import CreatorMatchingService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = CreatorMatchingService(db)
    creator = await _member(db, org)
    proj = await _project(db, org, owner)
    a = await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)

    # respond via the WRONG org → ASSIGNMENT_NOT_FOUND (kills the `is None or
    # wrong-org` -> `and` mutant on respond)
    with pytest.raises(AppError) as e_x:
        await svc.respond_assignment(a.id, other_org.id, creator.id, accept=True)
    assert e_x.value.code == "ASSIGNMENT_NOT_FOUND"

    # respond as someone who is not the offered creator → 403
    intruder = await _member(db, org)
    with pytest.raises(AppError) as e_own:
        await svc.respond_assignment(a.id, org.id, intruder.id, accept=True)
    assert e_own.value.code == "NOT_YOUR_ASSIGNMENT"

    # accept a now-ARCHIVED project → 409, not a live acceptance
    from app.models.project import ContentStatus

    proj.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError) as e_dead:
        await svc.respond_assignment(a.id, org.id, creator.id, accept=True)
    assert e_dead.value.code == "PROJECT_NOT_AVAILABLE"

    # decline still works on the (archived-project) offer, then double-respond 409
    declined = await svc.respond_assignment(a.id, org.id, creator.id, accept=False)
    assert declined.status == "declined"
    with pytest.raises(AppError) as e_again:
        await svc.respond_assignment(a.id, org.id, creator.id, accept=False)
    assert e_again.value.code == "ASSIGNMENT_ALREADY_RESPONDED"


async def test_withdraw_guards_r425(db):
    from app.services.creator_matching import CreatorMatchingService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = CreatorMatchingService(db)
    creator = await _member(db, org)
    proj = await _project(db, org, owner)
    a = await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)

    # withdraw via the WRONG org → ASSIGNMENT_NOT_FOUND (kills withdraw's
    # `is None or wrong-org` -> `and` mutant)
    with pytest.raises(AppError) as e_x:
        await svc.withdraw_assignment(a.id, other_org.id)
    assert e_x.value.code == "ASSIGNMENT_NOT_FOUND"

    # withdraw a pending offer → withdrawn; then re-offer reopens it
    w = await svc.withdraw_assignment(a.id, org.id)
    assert w.status == "withdrawn"
    reoffered = await svc.offer_assignment(org.id, proj.id, creator.id, owner.id)
    assert reoffered.id == a.id and reoffered.status == "offered"

    # accept it, then withdraw an ACCEPTED offer → 409 (only pending withdraws)
    await svc.respond_assignment(a.id, org.id, creator.id, accept=True)
    with pytest.raises(AppError) as e_acc:
        await svc.withdraw_assignment(a.id, org.id)
    assert e_acc.value.code == "ASSIGNMENT_ALREADY_RESPONDED"
