"""R444: skill-pack approval lifecycle — create public-gate (R60), submit/
approve/reject state machine, audit trail, creator notifications (R113[L2]).

Documented EQUIVALENT: 422->423 / 409->410 HTTP status-class swaps and
L484 reason[:500] -> [:501] truncation bound.
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.skill_pack import PackVisibility
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db):
    u = User(
        email=f"r444-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R444",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(
        name=f"R444 {uuid.uuid4().hex[:5]}",
        slug=f"r444-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return o


async def test_create_public_gate_r444(db):
    from app.services.skill_pack import SkillPackService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillPackService(db)

    # R60: creating directly with public visibility is refused
    with pytest.raises(AppError) as e_pub:
        await svc.create_pack(org.id, owner.id, name="P", visibility="public")
    assert e_pub.value.code == "APPROVAL_REQUIRED"
    # a normal (private) create succeeds with no review_status yet
    pack = await svc.create_pack(org.id, owner.id, name="P")
    assert pack.review_status is None
    assert pack.visibility != PackVisibility.PUBLIC


async def test_approval_state_machine_r444(db):
    from app.services.skill_pack import SkillPackService

    owner = await _user(db)
    org = await _org(db, owner)
    creator = await _user(db)
    svc = SkillPackService(db)
    reviewer = await _user(db)

    pack = await svc.create_pack(org.id, creator.id, name="Pack")

    # approve/reject before submit → NOT_PENDING (must be pending)
    with pytest.raises(AppError) as e_na:
        await svc.approve_pack(pack.id, org.id, reviewer.id)
    assert e_na.value.code == "NOT_PENDING"

    # submit → pending; a re-submit while pending → 409
    submitted = await svc.submit_for_review(pack.id, org.id, creator.id)
    assert submitted.review_status == "pending"
    with pytest.raises(AppError) as e_ap:
        await svc.submit_for_review(pack.id, org.id, creator.id)
    assert e_ap.value.code == "ALREADY_PENDING"

    # reject with a reason → rejected + reason stored + audit event
    rejected = await svc.reject_pack(pack.id, org.id, reason="needs polish", actor_id=reviewer.id)
    assert rejected.review_status == "rejected"
    assert rejected.rejection_reason == "needs polish"
    # a rejected pack can be re-submitted (not approved yet)
    await svc.submit_for_review(pack.id, org.id, creator.id)
    # approve → PUBLIC + approved + rejection_reason CLEARED (R84)
    approved = await svc.approve_pack(pack.id, org.id, reviewer.id)
    assert approved.review_status == "approved"
    assert approved.visibility == PackVisibility.PUBLIC
    assert approved.rejection_reason is None
    # cannot re-submit an approved pack
    with pytest.raises(AppError) as e_resub:
        await svc.submit_for_review(pack.id, org.id, creator.id)
    assert e_resub.value.code == "ALREADY_APPROVED"

    # the audit history is chronological (newest first): submitted, rejected,
    # submitted, approved
    history = await svc.list_approval_history(pack.id, org.id)
    actions = [h.action for h in history]
    assert actions == ["approved", "submitted", "rejected", "submitted"]

    # the creator was notified of the verdict (R113[L2]) — approve + reject
    from sqlalchemy import select

    from app.models.notification import Notification

    notifs = (
        (await db.execute(select(Notification).where(Notification.user_id == creator.id)))
        .scalars()
        .all()
    )
    types = {n.type for n in notifs}
    assert "pack.approved" in types
    assert "pack.rejected" in types


async def test_no_self_notification_r444(db):
    from sqlalchemy import select

    from app.models.notification import Notification
    from app.services.skill_pack import SkillPackService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = SkillPackService(db)
    # the creator reviews their OWN pack — no self-notification is created
    pack = await svc.create_pack(org.id, owner.id, name="Self")
    await svc.submit_for_review(pack.id, org.id, owner.id)
    await svc.approve_pack(pack.id, org.id, owner.id)  # actor == creator
    notifs = (
        (
            await db.execute(
                select(Notification).where(
                    Notification.user_id == owner.id, Notification.type == "pack.approved"
                )
            )
        )
        .scalars()
        .all()
    )
    assert notifs == []

    # a self-REJECT likewise creates no notification (kills the reject
    #  ->  mutant, which would
    # self-notify)
    pack2 = await svc.create_pack(org.id, owner.id, name="Self2")
    await svc.submit_for_review(pack2.id, org.id, owner.id)
    await svc.reject_pack(pack2.id, org.id, reason="nope", actor_id=owner.id)
    rej = (
        (
            await db.execute(
                select(Notification).where(
                    Notification.user_id == owner.id, Notification.type == "pack.rejected"
                )
            )
        )
        .scalars()
        .all()
    )
    assert rej == []
