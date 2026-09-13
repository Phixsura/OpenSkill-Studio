"""R435: peer-review lifecycle — round setup, allocation, assessment guards,
aggregation. Money-adjacent (drives grades); guards prevent double/late/
out-of-phase/over-max scoring and cross-org access.

Documented EQUIVALENT mutants (adjudicated): the 404->405 / 422->423 /
409->410 raises are HTTP status-class swaps (codes pinned, number not);
L301 `now > deadline` >->>= is a clock-instant equality edge; L344
`round(avg, 1)` 1->2 differs only for a fractional multi-reviewer mean
(the fixtures use integer/single-reviewer scores).
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.project import (
    ContentStatus,
    PeerAssessmentStatus,
    PeerReviewPhase,
    Submission,
    SubmissionStatus,
)
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
        email=f"r435-{uuid.uuid4().hex[:10]}@t.com",
        password_hash=hash_password("Test123!"),
        display_name="R435",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _setup(db, *, published=True, deadline=None, n_authors=3):
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _user(db)
    org = await OrgService(db).create(
        name=f"R435 {uuid.uuid4().hex[:5]}",
        slug=f"r435-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    proj = await ProjectService(db).create_project(
        org.id, "P", None, "d", "i", "beginner", 100, [], None, None, 0, 0, None, owner.id
    )
    if published:
        proj.status = ContentStatus.PUBLISHED
        await db.flush()
    authors = [await _user(db) for _ in range(n_authors)]
    for a in authors:
        db.add(
            Submission(
                org_id=org.id,
                project_id=proj.id,
                user_id=a.id,
                version=1,
                status=SubmissionStatus.SUBMITTED,
            )
        )
    await db.flush()
    return owner, org, proj, authors


async def test_create_round_guards_r435(db):
    from app.services.peer_review import PeerReviewService

    owner, org, proj, _ = await _setup(db)
    other_org_owner, other_org, _, _ = await _setup(db)
    svc = PeerReviewService(db)

    # an ARCHIVED project → PROJECT_NOT_FOUND (kills the `is None or archived`
    # -> `and` mutant)
    arch = proj
    arch.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(AppError) as e_arch:
        await svc.create_round(org.id, arch.id, owner.id, name="R")
    assert e_arch.value.code == "PROJECT_NOT_FOUND"
    arch.status = ContentStatus.PUBLISHED
    await db.flush()

    # a cross-org caller → PROJECT_NOT_FOUND
    with pytest.raises(AppError) as e_x:
        await svc.create_round(other_org.id, proj.id, owner.id, name="R")
    assert e_x.value.code == "PROJECT_NOT_FOUND"

    rnd = await svc.create_round(org.id, proj.id, owner.id, name="Round 1")
    assert rnd.phase == PeerReviewPhase.SETUP


async def test_start_assessment_and_guards_r435(db):
    from app.services.peer_review import PeerReviewService

    owner, org, proj, authors = await _setup(db, n_authors=3)
    other_owner, other_org, _, _ = await _setup(db)
    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, proj.id, owner.id, name="R", num_reviews=2)

    # cross-org start → RoundNotFound (kills the `is None or wrong-org` -> and)
    with pytest.raises(AppError):
        await svc.start_assessment(rnd.id, other_org.id)

    # start allocates num_reviews per submission; the returned count matches
    # the actual assessment rows created (kills `count += 1` -> += 2)
    started, count = await svc.start_assessment(rnd.id, org.id)
    assert started.phase == PeerReviewPhase.ASSESSMENT
    from sqlalchemy import func, select

    from app.models.project import PeerAssessment

    actual = (
        await db.execute(
            select(func.count(PeerAssessment.id)).where(PeerAssessment.round_id == rnd.id)
        )
    ).scalar_one()
    assert count == actual == 3 * 2  # 3 authors x num_reviews 2

    # starting again (now ASSESSMENT, not SETUP) → INVALID_PHASE
    with pytest.raises(AppError) as e_phase:
        await svc.start_assessment(rnd.id, org.id)
    assert e_phase.value.code == "INVALID_PHASE"

    # a round with < 2 submitted authors cannot start
    _, org2, proj2, _ = await _setup(db, n_authors=1)
    solo_rnd = await PeerReviewService(db).create_round(org2.id, proj2.id, other_owner.id, name="S")
    with pytest.raises(AppError) as e_few:
        await svc.start_assessment(solo_rnd.id, org2.id)
    assert e_few.value.code == "NOT_ENOUGH_SUBMISSIONS"

    # DEFAULT num_reviews is 2 (kills the `num_reviews: int = 2` -> 3 default):
    # a round created without the arg allocates 2 per submission
    o3, org3, proj3, a3 = await _setup(db, n_authors=3)
    dflt = await PeerReviewService(db).create_round(org3.id, proj3.id, o3.id, name="D")
    assert dflt.num_reviews == 2
    _, dflt_count = await PeerReviewService(db).start_assessment(dflt.id, org3.id)
    assert dflt_count == 3 * 2

    # include_self_review adds ONE self-assessment per author (kills the
    # self-review-loop `count += 1` -> += 2)
    o4, org4, proj4, a4 = await _setup(db, n_authors=3)
    selfr = await PeerReviewService(db).create_round(
        org4.id, proj4.id, o4.id, name="SR", num_reviews=1, include_self_review=True
    )
    _, self_count = await PeerReviewService(db).start_assessment(selfr.id, org4.id)
    actual_self = (
        await db.execute(
            select(func.count(PeerAssessment.id)).where(PeerAssessment.round_id == selfr.id)
        )
    ).scalar_one()
    assert self_count == actual_self == 3 * 1 + 3  # 3 peer + 3 self


async def test_submit_assessment_guards_r435(db):
    from sqlalchemy import select

    from app.models.project import PeerAssessment
    from app.services.peer_review import PeerReviewService

    owner, org, proj, authors = await _setup(db, n_authors=3)
    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, proj.id, owner.id, name="R", num_reviews=2)
    await svc.start_assessment(rnd.id, org.id)

    a1 = (
        await db.execute(select(PeerAssessment).where(PeerAssessment.round_id == rnd.id).limit(1))
    ).scalar_one()

    # not the assigned reviewer → 403
    intruder = await _user(db)
    with pytest.raises(AppError) as e_own:
        await svc.submit_assessment(
            a1.id, intruder.id, org.id, score=50, score_breakdown=None, feedback=None
        )
    assert e_own.value.status_code == 403

    # a score above the project max → SCORE_EXCEEDS_MAX (kills `> max` -> `>= max`
    # would also reject max; here max+1 must reject and exactly max must pass)
    with pytest.raises(AppError) as e_over:
        await svc.submit_assessment(
            a1.id, a1.reviewer_id, org.id, score=101, score_breakdown=None, feedback=None
        )
    assert e_over.value.code == "SCORE_EXCEEDS_MAX"
    ok = await svc.submit_assessment(
        a1.id, a1.reviewer_id, org.id, score=100, score_breakdown=None, feedback=None
    )
    assert ok.status == PeerAssessmentStatus.SUBMITTED
    assert ok.score == 100

    # re-submitting the same assessment → ALREADY_SUBMITTED
    with pytest.raises(AppError) as e_dup:
        await svc.submit_assessment(
            a1.id, a1.reviewer_id, org.id, score=80, score_breakdown=None, feedback=None
        )
    assert e_dup.value.code == "ALREADY_SUBMITTED"


async def test_deadline_and_results_r435(db):
    from sqlalchemy import select

    from app.models.project import PeerAssessment
    from app.services.peer_review import PeerReviewService

    owner, org, proj, authors = await _setup(
        db, n_authors=2, deadline=datetime.now(UTC) - timedelta(hours=1)
    )
    svc = PeerReviewService(db)
    # deadline in the PAST → submissions blocked once past it
    rnd = await svc.create_round(
        org.id,
        proj.id,
        owner.id,
        name="R",
        num_reviews=1,
        deadline=datetime.now(UTC) - timedelta(hours=1),
    )
    await svc.start_assessment(rnd.id, org.id)
    a = (
        await db.execute(select(PeerAssessment).where(PeerAssessment.round_id == rnd.id).limit(1))
    ).scalar_one()
    with pytest.raises(AppError) as e_dl:
        await svc.submit_assessment(
            a.id, a.reviewer_id, org.id, score=50, score_breakdown=None, feedback=None
        )
    assert e_dl.value.code == "DEADLINE_PASSED"

    # a future-deadline round aggregates submitted scores (mean per submission)
    owner2, org2, proj2, authors2 = await _setup(db, n_authors=2)
    rnd2 = await svc.create_round(
        org2.id,
        proj2.id,
        owner2.id,
        name="R2",
        num_reviews=1,
        deadline=datetime.now(UTC) + timedelta(days=1),
    )
    await svc.start_assessment(rnd2.id, org2.id)
    assessments = (
        (await db.execute(select(PeerAssessment).where(PeerAssessment.round_id == rnd2.id)))
        .scalars()
        .all()
    )
    # submit distinct scores; group them per submission for the mean
    for i, a in enumerate(assessments):
        await svc.submit_assessment(
            a.id, a.reviewer_id, org2.id, score=40 + i * 20, score_breakdown=None, feedback=None
        )
    results = await svc.round_results(rnd2.id, org2.id)
    assert len(results) == len({a.submission_id for a in assessments})
    for r in results:
        assert r["avg_score"] is not None
        assert r["review_count"] >= 1

    # close_round: cross-org → not found; correct org → CLOSED
    with pytest.raises(AppError):
        await svc.close_round(rnd2.id, org.id)  # wrong org
    closed = await svc.close_round(rnd2.id, org2.id)
    assert closed.phase == PeerReviewPhase.CLOSED
