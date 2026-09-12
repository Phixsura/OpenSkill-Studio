"""R433: gamification award idempotency, level math, leaderboard ranking.

award_points is the anti-abuse core (per-(user,org,reason,reference_id)
dedup stops review/resubmit ping-pong inflation); the leaderboard and
summaries must be org- and user-scoped.

Documented EQUIVALENT / defense-shadowed mutants (adjudicated):
- L112-L125 live in award_points' `except IntegrityError` concurrent-insert
  fallback (re-fetch the winner's row + atomic UPDATE) — reachable only when
  two sessions race the first insert, so a single-session test cannot
  exercise it; the main create + update paths ARE pinned by the
  accumulation test.
- L61 `.limit(1)` 1->2 on the dedup existence probe (scalar_one_or_none over
  at-most-one row — a larger limit returns the same first row).
- L157/L197 default limit 20->21 / 50->51 on leaderboard/history (both
  return all fixtures well under the cap).
"""

import uuid

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, name="U"):
    u = User(email=f"r433-{uuid.uuid4().hex[:10]}@t.com", password_hash=hash_password("Test123!"),
             display_name=name, role=UserRole.STUDENT, status=UserStatus.ACTIVE)
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    from app.services.organization import OrgService

    o = await OrgService(db).create(name=f"R433 {uuid.uuid4().hex[:5]}",
                                    slug=f"r433-{uuid.uuid4().hex[:10]}",
                                    description=None, created_by=owner.id)
    await db.flush()
    return o


async def test_award_idempotency_and_accumulation_r433(db):
    from app.services.gamification import GamificationService

    owner = await _user(db)
    org = await _org(db, owner)
    svc = GamificationService(db)
    u = await _user(db)

    # first award creates the aggregate
    await svc.award_points(u.id, org.id, 50, "project_submission", reference_id="sub-1")
    pts = await svc.get_user_points(u.id, org.id)
    assert pts["total_points"] == 50
    assert pts["level"] == 1  # 50 < 100

    # SAME (reason, reference_id) is idempotent — no double award
    await svc.award_points(u.id, org.id, 50, "project_submission", reference_id="sub-1")
    assert (await svc.get_user_points(u.id, org.id))["total_points"] == 50

    # a DIFFERENT reference_id accumulates and crosses a level boundary
    await svc.award_points(u.id, org.id, 60, "project_submission", reference_id="sub-2")
    pts2 = await svc.get_user_points(u.id, org.id)
    assert pts2["total_points"] == 110
    assert pts2["level"] == 2  # 110 // 100 + 1

    # a different REASON with the same reference_id is a distinct award
    await svc.award_points(u.id, org.id, 5, "review_posted", reference_id="sub-1")
    assert (await svc.get_user_points(u.id, org.id))["total_points"] == 115

    # award with NO reference_id is never deduped (each call adds)
    await svc.award_points(u.id, org.id, 10, "manual")
    await svc.award_points(u.id, org.id, 10, "manual")
    assert (await svc.get_user_points(u.id, org.id))["total_points"] == 135

    # history reflects each distinct ledger row (not the deduped repeat)
    hist = await svc.get_user_points_history(u.id, org.id)
    reasons = [h["reason"] for h in hist]
    assert reasons.count("project_submission") == 2  # sub-1 + sub-2, not 3
    assert reasons.count("manual") == 2


async def test_award_scoping_r433(db):
    from app.services.gamification import GamificationService

    owner = await _user(db)
    org_a = await _org(db, owner)
    org_b = await _org(db, owner)
    svc = GamificationService(db)
    u = await _user(db)

    # the SAME reference_id in a DIFFERENT org is a separate award (dedup is
    # org-scoped)
    await svc.award_points(u.id, org_a.id, 30, "project_submission", reference_id="x")
    await svc.award_points(u.id, org_b.id, 40, "project_submission", reference_id="x")
    assert (await svc.get_user_points(u.id, org_a.id))["total_points"] == 30
    assert (await svc.get_user_points(u.id, org_b.id))["total_points"] == 40

    # an unknown user/org summary is zero, level 1 (not a crash)
    stranger = await _user(db)
    assert await svc.get_user_points(stranger.id, org_a.id) == {"total_points": 0, "level": 1}


async def test_leaderboard_ranking_r433(db):
    from app.services.gamification import GamificationService

    owner = await _user(db)
    org = await _org(db, owner)
    other_org = await _org(db, owner)
    svc = GamificationService(db)
    top = await _user(db, "Top")
    mid = await _user(db, "Mid")
    low = await _user(db, "Low")

    await svc.award_points(top.id, org.id, 300, "manual")
    await svc.award_points(mid.id, org.id, 200, "manual")
    await svc.award_points(low.id, org.id, 100, "manual")
    # a high scorer in ANOTHER org must not appear in this org's board
    await svc.award_points(await _then_id(db, "Ghost"), other_org.id, 999, "manual")

    board = await svc.get_leaderboard(org.id)
    assert [r["display_name"] for r in board] == ["Top", "Mid", "Low"]
    # rank is 1-based and in descending points order
    assert [r["rank"] for r in board] == [1, 2, 3]
    assert [r["total_points"] for r in board] == [300, 200, 100]

    # limit truncates to the top N
    top2 = await svc.get_leaderboard(org.id, limit=2)
    assert [r["display_name"] for r in top2] == ["Top", "Mid"]


async def _then_id(db, name):
    u = await _user(db, name)
    return u.id
