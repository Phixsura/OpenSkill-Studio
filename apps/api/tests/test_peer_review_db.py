"""DB integration tests for peer review lifecycle.

APP_ENV=test PYTHONPATH=. uv run pytest tests/test_peer_review_db.py -v
"""

import uuid

import pytest
import pytest_asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole
from app.models.user import User, UserRole, UserStatus
from app.services.peer_review import PeerReviewService
from app.services.project import ProjectService


@pytest_asyncio.fixture
async def db():
    from app.core.database import engine

    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, name="Peer"):
    u = User(
        email=f"peer-{uuid.uuid4().hex[:8]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name=name,
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org(db, owner):
    # Issue #27: organizations.tenant_id is NOT NULL — create the owning tenant
    from app.controlplane.services.audit import Actor
    from app.controlplane.services.tenants import create_tenant

    tenant = await create_tenant(
        db,
        name=f"PeerTenant-{uuid.uuid4().hex[:6]}",
        slug=f"peer-t-{uuid.uuid4().hex[:8]}",
        actor=Actor(user_id=owner.id, type="tenant"),
        owner_user_id=owner.id,
    )
    org = Organization(
        name=f"PeerOrg-{uuid.uuid4().hex[:6]}",
        slug=f"peer-{uuid.uuid4().hex[:8]}",
        created_by=owner.id,
        tenant_id=tenant.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=owner.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await db.flush()
    return org


async def _submitted_project(db, org, instructor, learners):
    """Project with one SUBMITTED submission per learner."""
    psvc = ProjectService(db)
    project = await psvc.create_project(
        org_id=org.id,
        title=f"Peer Project {uuid.uuid4().hex[:6]}",
        slug=None,
        description="d",
        instructions="i",
        difficulty="beginner",
        max_score=100,
        rubric=[{"criterion": "Quality", "max_score": 100}],
        deadline=None,
        late_deadline=None,
        late_penalty_pct=0,
        max_submissions=0,
        skill_ids=None,
        created_by=instructor.id,
    )
    d = await psvc.create_deliverable(project.id, "Work", None, "text", True, {}, 0)
    subs = {}
    for learner in learners:
        db.add(
            OrgMember(
                org_id=org.id,
                user_id=learner.id,
                role=OrgRole.STUDENT,
                status=MemberStatus.ACTIVE,
            )
        )
        await db.flush()
        sub = await psvc.create_submission(org.id, project.id, learner.id)
        from app.models.project import ItemType, SubmissionItem

        db.add(
            SubmissionItem(
                submission_id=sub.id,
                deliverable_id=d.id,
                type=ItemType.TEXT,
                content=f"work by {learner.display_name}",
            )
        )
        await db.flush()
        await psvc.submit_draft(sub.id, learner.id)
        subs[learner.id] = sub
    return project, subs


@pytest.mark.asyncio
async def test_round_lifecycle_full(db):
    """setup → allocate → assess → close → aggregate."""
    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, f"L{i}") for i in range(4)]
    project, subs = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, project.id, instructor.id, name="Round 1", num_reviews=2)
    assert rnd.phase.value == "setup"

    rnd, count = await svc.start_assessment(rnd.id, org.id)
    assert rnd.phase.value == "assessment"
    assert count == 8  # 4 reviewers × 2 reviews

    # Every learner has exactly 2 assessments, none their own
    for learner in learners:
        mine = await svc.my_assessments(rnd.id, learner.id)
        assert len(mine) == 2
        for a in mine:
            assert a.submission_id != subs[learner.id].id

    # All learners submit their assessments
    for learner in learners:
        for a in await svc.my_assessments(rnd.id, learner.id):
            await svc.submit_assessment(
                a.id,
                learner.id,
                org.id,
                score=80,
                score_breakdown=[{"criterion": "Quality", "score": 80}],
                feedback="solid work",
            )

    results = await svc.round_results(rnd.id, org.id)
    assert len(results) == 4  # every submission reviewed (≥1 guarantee)
    total_reviews = sum(r["review_count"] for r in results)
    assert total_reviews == 8  # 4 reviewers × 2 reviews each
    for r in results:
        assert r["avg_score"] == 80.0
        assert r["review_count"] >= 1  # fairness floor; exact split may vary

    rnd = await svc.close_round(rnd.id, org.id)
    assert rnd.phase.value == "closed"


@pytest.mark.asyncio
async def test_not_enough_submissions(db):
    from app.exceptions import AppError

    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, "Solo")]
    project, _ = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, project.id, instructor.id, name="R", num_reviews=2)
    with pytest.raises(AppError) as exc:
        await svc.start_assessment(rnd.id, org.id)
    assert exc.value.code == "NOT_ENOUGH_SUBMISSIONS"


@pytest.mark.asyncio
async def test_self_review_included(db):
    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, f"S{i}") for i in range(3)]
    project, subs = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(
        org.id,
        project.id,
        instructor.id,
        name="R",
        num_reviews=1,
        include_self_review=True,
    )
    _, count = await svc.start_assessment(rnd.id, org.id)
    assert count == 6  # 3 peer + 3 self

    for learner in learners:
        mine = await svc.my_assessments(rnd.id, learner.id)
        selfs = [a for a in mine if a.is_self_review]
        assert len(selfs) == 1
        assert selfs[0].submission_id == subs[learner.id].id


@pytest.mark.asyncio
async def test_cannot_submit_other_reviewers_assessment(db):
    from app.exceptions import AppError

    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, f"X{i}") for i in range(2)]
    project, _ = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, project.id, instructor.id, name="R", num_reviews=1)
    await svc.start_assessment(rnd.id, org.id)

    a = (await svc.my_assessments(rnd.id, learners[0].id))[0]
    with pytest.raises(AppError) as exc:
        await svc.submit_assessment(
            a.id, learners[1].id, org.id, score=50, score_breakdown=None, feedback=None
        )
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_cannot_assess_after_close(db):
    from app.exceptions import AppError

    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, f"C{i}") for i in range(2)]
    project, _ = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(org.id, project.id, instructor.id, name="R", num_reviews=1)
    await svc.start_assessment(rnd.id, org.id)
    a = (await svc.my_assessments(rnd.id, learners[0].id))[0]
    await svc.close_round(rnd.id, org.id)

    with pytest.raises(AppError) as exc:
        await svc.submit_assessment(
            a.id, learners[0].id, org.id, score=50, score_breakdown=None, feedback=None
        )
    assert exc.value.code == "INVALID_PHASE"


@pytest.mark.asyncio
async def test_round_org_isolation(db):
    from app.exceptions import AppError
    from app.services.peer_review import RoundNotFoundError

    instructor = await _user(db, "Inst")
    org_a = await _org(db, instructor)
    learners = [await _user(db, f"I{i}") for i in range(2)]
    project, _ = await _submitted_project(db, org_a, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(org_a.id, project.id, instructor.id, name="R", num_reviews=1)

    other = await _user(db, "OtherOwner")
    org_b = await _org(db, other)
    with pytest.raises((AppError, RoundNotFoundError)):
        await svc.get_round(rnd.id, org_b.id)


@pytest.mark.asyncio
async def test_self_reviews_excluded_from_aggregate(db):
    instructor = await _user(db, "Inst")
    org = await _org(db, instructor)
    learners = [await _user(db, f"A{i}") for i in range(2)]
    project, _ = await _submitted_project(db, org, instructor, learners)

    svc = PeerReviewService(db)
    rnd = await svc.create_round(
        org.id,
        project.id,
        instructor.id,
        name="R",
        num_reviews=1,
        include_self_review=True,
    )
    await svc.start_assessment(rnd.id, org.id)

    # Submit peer reviews at 60, self reviews at 100
    for learner in learners:
        for a in await svc.my_assessments(rnd.id, learner.id):
            score = 100 if a.is_self_review else 60
            await svc.submit_assessment(
                a.id, learner.id, org.id, score=score, score_breakdown=None, feedback=None
            )

    results = await svc.round_results(rnd.id, org.id)
    for r in results:
        assert r["avg_score"] == 60.0  # self scores excluded
        assert r["review_count"] == 1


def test_allocation_fairness_exact():
    """R202 (AST-mutation survivors in allocate_reviews): pin the fairness
    kernel the lifecycle tests never asserted — progressive rounds (everyone
    gets 1 before anyone gets 2), per-reviewer dedupe, no self-review, and
    the orphan-repair donor floor (donor keeps >= 1)."""
    import random

    from app.services.peer_review import allocate_reviews

    subs = {f"s{i}": f"u{i}" for i in range(5)}
    reviewers = [f"u{i}" for i in range(5)]
    rng = random.Random(42)
    pairs = allocate_reviews(subs, reviewers, 2, rng=rng)

    # Each reviewer exactly num_reviews assignments (5 subs, self excluded → feasible)
    per_reviewer = {}
    for r, s in pairs:
        per_reviewer.setdefault(r, []).append(s)
        assert subs[s] != r, "self-review pair"
    assert all(len(v) == 2 for v in per_reviewer.values()), per_reviewer
    # No duplicate (reviewer, submission) pair
    assert len(set(pairs)) == len(pairs)
    # Every submission reviewed at least once (repair guarantees coverage here)
    reviewed = {s for _, s in pairs}
    assert reviewed == set(subs), reviewed

    # Degenerate guards (kills the L59 Or→And / LtE→Lt survivors)
    assert allocate_reviews(subs, reviewers, 0, rng=rng) == []
    assert allocate_reviews({}, reviewers, 2, rng=rng) == []
    assert allocate_reviews(subs, [], 2, rng=rng) == []

    # Two-party edge: 1 review each, mutual — repair must not create dupes
    two = allocate_reviews({"sa": "ua", "sb": "ub"}, ["ua", "ub"], 1, rng=random.Random(7))
    assert sorted(two) == [("ua", "sb"), ("ub", "sa")]


def test_allocation_repair_swap_path():
    """R202 wave-1b: the orphan-REPAIR block had zero test reach (all its
    mutants survived — even index constants inside the sort key). Seed 0
    forces it: uA's rng pick takes s1 first, stranding sO (authored by uB,
    who can only take s1) with donor load 2 → repair swaps (uA,s1)→(uA,sO)."""
    import random

    from app.services.peer_review import allocate_reviews

    pairs = allocate_reviews({"sO": "uB", "s1": "u9"}, ["uA", "uB"], 1, rng=random.Random(0))
    assert sorted(pairs) == [("uA", "sO"), ("uB", "s1")], pairs

    # Donor floor (load > 1, strictly): with a single load-1 donor the swap
    # must NOT run — stealing its only review just moves the orphan.
    pairs = allocate_reviews({"sO": "uA", "sX": "u9"}, ["uA"], 1, rng=random.Random(0))
    assert pairs == [("uA", "sX")], "load-1 donor must be left alone"

    # Distribution: reviewer-side fairness is the guarantee (each reviewer
    # exactly num_reviews); submission-side balance is best-effort ONLY
    # (self-exclusion can legally yield a 3/1 spread — verified live), and
    # the repair pass fixes zero-review orphans, not imbalance. Assert the
    # real contract: total pairs and full coverage.
    from collections import Counter

    subs = {f"s{i}": f"u{i}" for i in range(5)}
    pairs = allocate_reviews(subs, [f"u{i}" for i in range(5)], 2, rng=random.Random(42))
    dist = Counter(s for _, s in pairs)
    assert sum(dist.values()) == 10 and set(dist) == set(subs), dist
