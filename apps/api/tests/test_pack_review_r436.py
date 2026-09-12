"""R436: pack review/rating service — self-review gate, stats recalc,
distribution histogram, helpful-vote toggle, ownership guards.

Documented EQUIVALENT mutants (adjudicated): 422->423 / 409->410 / 404->405
HTTP status-class swaps; L286/L306 helpful_count decrement by 1 vs 2 (greatest(0, ...)
clamps at 0, so from a count of 1 both land on 0); L258/L332 round
precision 2->3 (fractional 3-decimal averages don't arise in the fixtures).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.organization import OrgRole
from app.models.skill_pack import PackStatus, PackVisibility, SkillPack
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
    u = User(email=f"r436-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name="R436", role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(name=f"R436 {uuid.uuid4().hex[:5]}",
                                    slug=f"r436-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o


async def _pack(db, org, creator, *, status=PackStatus.PUBLISHED, vis=PackVisibility.PUBLIC):
    p = SkillPack(owner_org_id=org.id, name="P", slug=f"p-{uuid.uuid4().hex[:10]}",
                  created_by=creator.id, status=status, visibility=vis)
    db.add(p)
    await db.flush()
    return p


async def test_create_review_gates_and_stats_r436(db):
    from app.services.pack_review import PackReviewService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = PackReviewService(db)
    creator = await _user(db)
    from app.services.organization import OrgService
    await OrgService(db).add_member(org.id, creator.id, OrgRole.STUDENT)
    pack = await _pack(db, org, creator)

    # the pack CREATOR cannot review their own pack
    with pytest.raises(AppError) as e_self:
        await svc.create_review(pack.id, creator.id, 5)
    assert e_self.value.code == "SELF_REVIEW_FORBIDDEN"

    # ANY active member of the owning org is also blocked (rating-inflation)
    org_member = await _user(db)
    await OrgService(db).add_member(org.id, org_member.id, OrgRole.STUDENT)
    with pytest.raises(AppError) as e_mem:
        await svc.create_review(pack.id, org_member.id, 5)
    assert e_mem.value.code == "SELF_REVIEW_FORBIDDEN"

    # an outside reviewer can; stats recalc (avg + count)
    r1 = await _user(db)
    await svc.create_review(pack.id, r1.id, 4, body="Good pack " * 3)
    await db.refresh(pack)
    assert pack.review_count == 1
    assert float(pack.average_rating) == 4.0

    # a second outside reviewer moves the average
    r2 = await _user(db)
    await svc.create_review(pack.id, r2.id, 2, body="Needs work here for sure")
    await db.refresh(pack)
    assert pack.review_count == 2
    assert float(pack.average_rating) == 3.0  # (4 + 2) / 2

    # a duplicate review by the same user → 409
    with pytest.raises(AppError) as e_dup:
        await svc.create_review(pack.id, r1.id, 5)
    assert e_dup.value.code == "DUPLICATE_REVIEW"

    # reviews on a non-published pack are refused
    draft_pack = await _pack(db, org, creator, status=PackStatus.DRAFT)
    with pytest.raises(AppError) as e_np:
        await svc.create_review(draft_pack.id, r1.id, 5)
    assert e_np.value.code == "PACK_NOT_FOUND"
    priv_pack = await _pack(db, org, creator, vis=PackVisibility.PRIVATE)
    with pytest.raises(AppError):
        await svc.create_review(priv_pack.id, r1.id, 5)


async def test_update_review_low_rating_body_gate_r436(db):
    from app.services.pack_review import PackReviewService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = PackReviewService(db)
    creator = await _user(db)
    pack = await _pack(db, org, creator)
    reviewer, intruder = await _user(db), await _user(db)
    r = await svc.create_review(pack.id, reviewer.id, 5, body="Great work on this")

    # a non-author cannot edit
    with pytest.raises(AppError) as e_own:
        await svc.update_review(r.id, intruder.id, rating=1, body="x" * 30)
    assert e_own.value.status_code == 403

    # lowering to <= 2 WITHOUT a substantive body (>=20 chars) is rejected
    with pytest.raises(AppError) as e_low:
        await svc.update_review(r.id, reviewer.id, rating=2, body="too short")
    assert e_low.value.status_code == 422
    # exactly rating 2 with a 20-char body is allowed; stats recalc
    updated = await svc.update_review(r.id, reviewer.id, rating=2, body="x" * 20)
    assert updated.rating == 2
    await db.refresh(pack)
    assert float(pack.average_rating) == 2.0
    # rating 3 needs NO substantive body (kills the `<= 2` -> `<= 3` threshold)
    up3 = await svc.update_review(r.id, reviewer.id, rating=3, body="ok")
    assert up3.rating == 3
    # a WRONG pack_id scopes the review out → ReviewNotFound (kills the
    # `review.pack_id != pack_id` -> `==` mutant)
    from app.services.pack_review import ReviewNotFoundError

    other_pack = await _pack(db, org, creator)
    with pytest.raises(ReviewNotFoundError):
        await svc.update_review(r.id, reviewer.id, rating=5, pack_id=other_pack.id)


async def test_distribution_and_helpful_and_delete_r436(db):
    from app.services.pack_review import PackReviewService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = PackReviewService(db)
    creator = await _user(db)
    pack = await _pack(db, org, creator)

    reviewers = [await _user(db) for _ in range(4)]
    for u, rating in zip(reviewers, [5, 5, 3, 1], strict=True):
        body = "detailed feedback here" if rating <= 2 else None
        await svc.create_review(pack.id, u.id, rating, body=body)

    dist = await svc.get_distribution(pack.id)
    assert dist["total"] == 4
    assert dist["distribution"] == {1: 1, 2: 0, 3: 1, 4: 0, 5: 2}
    assert dist["average"] == round((5 + 5 + 3 + 1) / 4, 2)  # 3.5

    # helpful vote toggles up then back down; never below 0
    from sqlalchemy import select

    from app.models.pack_review import PackReview

    a_review = (await db.execute(
        select(PackReview).where(PackReview.pack_id == pack.id).limit(1))
    ).scalar_one()
    voter = await _user(db)
    v1 = await svc.toggle_helpful(a_review.id, voter.id)
    assert v1.helpful_count == 1
    v2 = await svc.toggle_helpful(a_review.id, voter.id)  # same user toggles off
    assert v2.helpful_count == 0

    # delete a review recomputes stats down
    before = (await svc.get_stats(pack.id))["review_count"]
    await svc.delete_review(a_review.id, a_review.user_id, pack.id)
    after = (await svc.get_stats(pack.id))["review_count"]
    assert after == before - 1

    # deleting someone else's review → 403
    other_review = (await db.execute(
        select(PackReview).where(PackReview.pack_id == pack.id).limit(1))
    ).scalar_one()
    intruder = await _user(db)
    with pytest.raises(AppError) as e_del:
        await svc.delete_review(other_review.id, intruder.id, pack.id)
    assert e_del.value.status_code == 403
    # a WRONG pack_id scopes the review out of delete → ReviewNotFound (kills
    # the delete `review.pack_id != pack_id` -> `==` mutant)
    from app.services.pack_review import ReviewNotFoundError

    owner2 = await _user(db)
    org_b = await _org(db, owner2)
    pack_b = await _pack(db, org_b, owner2)
    with pytest.raises(ReviewNotFoundError):
        await svc.delete_review(other_review.id, other_review.user_id, pack_b.id)


async def test_distribution_edges_r436(db):
    from app.services.pack_review import PackReviewService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = PackReviewService(db)
    creator = await _user(db)

    # a pack with NO reviews: total 0, average None (kills the `total > 0`
    # -> `>= 0` mutant, which would ZeroDivisionError on 0/0)
    empty = await _pack(db, org, creator)
    dist0 = await svc.get_distribution(empty.id)
    assert dist0["total"] == 0
    assert dist0["average"] is None
    assert dist0["distribution"] == {1: 0, 2: 0, 3: 0, 4: 0, 5: 2 - 2}  # all zeros

    # a pack with only high ratings still reports the 1-star bucket as 0
    # (kills the distribution init `range(1, 6)` -> `range(2, 6)` mutant, which
    # would omit the 1 key entirely)
    pack = await _pack(db, org, creator)
    for rating in (5, 4):
        await svc.create_review(pack.id, (await _user(db)).id, rating)
    dist = await svc.get_distribution(pack.id)
    assert dist["distribution"] == {1: 0, 2: 0, 3: 0, 4: 1, 5: 1}


async def test_reply_owner_only_r436(db):
    from app.services.pack_review import PackReviewService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = PackReviewService(db)
    creator = await _user(db)
    pack = await _pack(db, org, creator)
    reviewer = await _user(db)
    r = await svc.create_review(pack.id, reviewer.id, 4, body="Nice pack here")

    # only the pack CREATOR may reply
    with pytest.raises(AppError) as e_own:
        await svc.reply_to_review(r.id, pack.id, reviewer.id, "thanks")
    assert e_own.value.status_code == 403
    replied = await svc.reply_to_review(r.id, pack.id, creator.id, "Thanks for the feedback!")
    assert replied.reply_text == "Thanks for the feedback!"
