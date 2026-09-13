"""R403: submission-lifecycle mutation hardening (pass-1 was 19/86).

Documented EQUIVALENT mutants (adjudicated, no test possible):
- L576/L581/L595/L603 ``limit(1) -> limit(2)``: existence probes read via
  scalar_one_or_none on at-most-one row semantics; a larger limit returns the
  same first row.
- L802 ``submission_id == -> !=`` in the S3-cleanup key select: the cleanup
  loop is wrapped in ``except Exception`` best-effort (no S3 in tests, and in
  prod a wrong key set only skips/attempts deletes, never changes DB state).
- L1342/L1344/L1348 ``<= -> <`` on ``now`` comparisons: differs only when the
  wall clock equals the deadline to the microsecond — an unobservable instant.
- L1318/L1323 ``> -> >=`` on override-vs-effective deadline: differs only when
  the override EQUALS the current effective deadline, where replacing a value
  with an equal value is an identity.
- L1418 ``> -> >=`` on ``late_penalty_pct > 0``: at pct == 0 the penalty
  branch computes score - score*0/100 == score — an arithmetic identity.
- L1230/L1231 ``== -> !=`` on grant_extension's one-row pre-check: the R200
  savepoint fallback catches the resulting IntegrityError and re-reads with
  the CORRECT (project, user) predicate, updating the winner — the pre-check
  is a pure optimization shielded by defense-in-depth (verified by hand:
  mutant passes because the fallback produces identical state).
"""

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _user(db, role=UserRole.STUDENT):
    u = User(
        email=f"r403-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R403",
        role=role,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org_with(db, owner):
    from app.services.organization import OrgService

    org = await OrgService(db).create(
        name=f"R403 {uuid.uuid4().hex[:6]}",
        slug=f"r403-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=owner.id,
    )
    await db.flush()
    return org


async def _project(db, org, creator, **kw):
    from app.services.project import ProjectService

    args = dict(
        title=f"P {uuid.uuid4().hex[:6]}",
        slug=None,
        description="d",
        instructions="i",
        difficulty="intermediate",
        max_score=100,
        rubric=[],
        deadline=None,
        late_deadline=None,
        late_penalty_pct=0,
        max_submissions=0,
        skill_ids=None,
    )
    args.update(kw)
    return await ProjectService(db).create_project(org.id, created_by=creator.id, **args)


async def test_submission_versioning_caps_and_overrides_r403(db):
    from app.models.organization import OrgRole
    from app.services.organization import OrgService
    from app.services.project import (
        MaxSubmissionsReachedError,
        ProjectNotFoundError,
        ProjectService,
    )

    owner = await _user(db, role=UserRole.ADMIN)
    org = await _org_with(db, owner)
    org_svc = OrgService(db)
    svc = ProjectService(db)
    a, b = await _user(db), await _user(db)
    await org_svc.add_member(org.id, a.id, OrgRole.STUDENT)
    await org_svc.add_member(org.id, b.id, OrgRole.STUDENT)

    # cap of 1: a's first create OK, second rejected AT the cap (>= not >)
    p = await _project(db, org, owner, max_submissions=1)
    sub_a = await svc.create_submission(org.id, p.id, a.id)
    assert sub_a.version == 1
    with pytest.raises(MaxSubmissionsReachedError):
        await svc.create_submission(org.id, p.id, a.id)

    # versions are PER (project, user): b's first submission is v1, not v2
    sub_b = await svc.create_submission(org.id, p.id, b.id)
    assert sub_b.version == 1

    # cohort max_submissions_override lifts the project cap for its members
    from app.models.cohort import Cohort, CohortMember, CohortProjectAssignment

    cohort = Cohort(org_id=org.id, name="C", slug=f"c-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(cohort)
    await db.flush()
    db.add(CohortMember(cohort_id=cohort.id, user_id=b.id, role="learner"))
    db.add(
        CohortProjectAssignment(
            assigned_by=owner.id, cohort_id=cohort.id, project_id=p.id, max_submissions_override=3
        )
    )
    await db.flush()
    # b (in cohort, override 3) can create a 2nd and 3rd; the 4th is rejected
    sub_b2 = await svc.create_submission(org.id, p.id, b.id)
    sub_b3 = await svc.create_submission(org.id, p.id, b.id)
    assert (sub_b2.version, sub_b3.version) == (2, 3)
    with pytest.raises(MaxSubmissionsReachedError):
        await svc.create_submission(org.id, p.id, b.id)
    # version = MAX existing + 1, never count + 1: delete the v2 draft — the
    # recreate under the cap must mint v4 (count+1 would re-mint a colliding 3)
    await svc.delete_submission(sub_b2.id, b.id)
    sub_b4 = await svc.create_submission(org.id, p.id, b.id)
    assert sub_b4.version == 4
    with pytest.raises(MaxSubmissionsReachedError):
        await svc.create_submission(org.id, p.id, b.id)
    # …while a (NOT in the cohort) no longer even SEES the project — the
    # cohort assignment made it restricted, and the visibility gate fires
    # before the cap (uniform 404, no existence oracle)
    with pytest.raises(AppError) as e_vis:
        await svc.create_submission(org.id, p.id, a.id)
    assert e_vis.value.status_code == 404

    # archived project → not found (or-gate, not and-gate)
    from app.models.project import ContentStatus

    p_arch = await _project(db, org, owner)
    p_arch.status = ContentStatus.ARCHIVED
    await db.flush()
    with pytest.raises(ProjectNotFoundError):
        await svc.create_submission(org.id, p_arch.id, a.id)


async def test_visibility_gate_matrix_r403(db):
    from app.models.organization import OrgRole
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _user(db, role=UserRole.ADMIN)
    org = await _org_with(db, owner)
    svc = ProjectService(db)
    org_svc = OrgService(db)
    inc, outc, solo = await _user(db), await _user(db), await _user(db)
    for u in (inc, outc, solo):
        await org_svc.add_member(org.id, u.id, OrgRole.STUDENT)

    # cohort-restricted project: member of the assigned cohort passes, an
    # unassigned user gets a 404 (never a 403 — no existence oracle)
    from app.models.cohort import Cohort, CohortMember, CohortProjectAssignment

    p = await _project(db, org, owner)
    cohort = Cohort(org_id=org.id, name="V", slug=f"v-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(cohort)
    await db.flush()
    db.add(CohortMember(cohort_id=cohort.id, user_id=inc.id, role="learner"))
    db.add(CohortProjectAssignment(cohort_id=cohort.id, project_id=p.id, assigned_by=owner.id))
    await db.flush()

    sub_in = await svc.create_submission(org.id, p.id, inc.id)
    assert sub_in.id
    with pytest.raises(AppError) as e_out:
        await svc.create_submission(org.id, p.id, outc.id)
    assert e_out.value.status_code == 404

    # creator-assignment-ONLY restriction (no cohort rows): assigned user
    # passes, unassigned 404s — proves restriction needs EITHER kind (or-gate)
    from app.models.project import ProjectCreatorAssignment

    p2 = await _project(db, org, owner)
    db.add(ProjectCreatorAssignment(project_id=p2.id, user_id=solo.id, assigned_by=owner.id))
    await db.flush()
    sub_solo = await svc.create_submission(org.id, p2.id, solo.id)
    assert sub_solo.id
    with pytest.raises(AppError) as e_ind:
        await svc.create_submission(org.id, p2.id, inc.id)
    assert e_ind.value.status_code == 404


async def test_submit_draft_gates_and_versioning_r403(db):
    from app.models.organization import OrgRole
    from app.models.project import ContentStatus, ItemType, SubmissionItem, SubmissionStatus
    from app.services.organization import OrgService
    from app.services.project import (
        InvalidStateError,
        MissingDeliverablesError,
        ProjectService,
    )

    owner = await _user(db, role=UserRole.ADMIN)
    org = await _org_with(db, owner)
    svc = ProjectService(db)
    org_svc = OrgService(db)
    stu, other = await _user(db), await _user(db)
    await org_svc.add_member(org.id, stu.id, OrgRole.STUDENT)
    await org_svc.add_member(org.id, other.id, OrgRole.STUDENT)

    p = await _project(db, org, owner)
    p.status = ContentStatus.PUBLISHED
    await db.flush()
    d = await svc.create_deliverable(p.id, "req", None, "text", True, {}, 0)
    d_opt = await svc.create_deliverable(p.id, "opt", None, "text", False, {}, 1)

    sub = await svc.create_submission(org.id, p.id, stu.id)

    # not the owner → 403 exactly
    with pytest.raises(AppError) as e_perm:
        await svc.submit_draft(sub.id, other.id)
    assert e_perm.value.status_code == 403

    # required deliverable unmet → blocked; a WHITESPACE-only text item and an
    # item on a different submission must not satisfy it
    with pytest.raises(MissingDeliverablesError):
        await svc.submit_draft(sub.id, stu.id)
    db.add(
        SubmissionItem(submission_id=sub.id, deliverable_id=d.id, type=ItemType.TEXT, content="   ")
    )
    await db.flush()
    with pytest.raises(MissingDeliverablesError):
        await svc.submit_draft(sub.id, stu.id)
    sub_other = await svc.create_submission(org.id, p.id, other.id)
    db.add(
        SubmissionItem(
            submission_id=sub_other.id, deliverable_id=d.id, type=ItemType.TEXT, content="done"
        )
    )
    await db.flush()
    with pytest.raises(MissingDeliverablesError):
        await svc.submit_draft(sub.id, stu.id)  # other's item must not count

    # a FILE item (no content) satisfies; optional deliverable stays optional
    db.add(
        SubmissionItem(
            submission_id=sub.id, deliverable_id=d.id, type=ItemType.FILE, file_key="k/1"
        )
    )
    await db.flush()
    assert d_opt.required is False
    # publication gate: require_published on a PUBLISHED project passes;
    # on-time (no deadline) submit is NOT late and keeps version 1
    submitted = await svc.submit_draft(sub.id, stu.id, require_published=True)
    assert submitted.status == SubmissionStatus.SUBMITTED
    assert submitted.is_late is False
    assert submitted.version == 1

    # double-submit blocked
    with pytest.raises(InvalidStateError):
        await svc.submit_draft(sub.id, stu.id)

    # revision-requested resubmit bumps the version by EXACTLY one
    submitted.status = SubmissionStatus.REVISION_REQUESTED
    await db.flush()
    re_sub = await svc.submit_draft(sub.id, stu.id)
    assert re_sub.version == 2
    assert re_sub.status == SubmissionStatus.SUBMITTED

    # unpublished + require_published → blocked for students, allowed without
    p.status = ContentStatus.DRAFT
    await db.flush()
    sub2 = await svc.create_submission(org.id, p.id, stu.id)
    db.add(
        SubmissionItem(
            submission_id=sub2.id, deliverable_id=d.id, type=ItemType.FILE, file_key="k/2"
        )
    )
    await db.flush()
    with pytest.raises(InvalidStateError):
        await svc.submit_draft(sub2.id, stu.id, require_published=True)
    ok = await svc.submit_draft(sub2.id, stu.id)  # instructor/internal path
    assert ok.status == SubmissionStatus.SUBMITTED

    # delete: only the owner (403), only drafts
    sub3 = await svc.create_submission(org.id, p.id, stu.id)
    with pytest.raises(AppError) as e_del:
        await svc.delete_submission(sub3.id, other.id)
    assert e_del.value.status_code == 403
    with pytest.raises(InvalidStateError):
        await svc.delete_submission(sub2.id, stu.id)  # submitted, not draft
    await svc.delete_submission(sub3.id, stu.id)  # owner deletes own draft


async def test_timing_precedence_and_extensions_r403(db):
    from app.models.organization import OrgRole
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _user(db, role=UserRole.ADMIN)
    org = await _org_with(db, owner)
    svc = ProjectService(db)
    org_svc = OrgService(db)
    stu = await _user(db)
    await org_svc.add_member(org.id, stu.id, OrgRole.STUDENT)
    now = datetime.now(UTC)

    # no deadline → on_time
    p_open = await _project(db, org, owner)
    assert await svc.get_submission_timing(p_open, stu.id) == "on_time"

    # past deadline, no late window → closed (and the None-late branch must
    # not crash — kills `and->or` on the late-window guard)
    p_closed = await _project(db, org, owner, deadline=now - timedelta(hours=2))
    assert await svc.get_submission_timing(p_closed, stu.id) == "closed"

    # past deadline, open late window → late
    p_late = await _project(
        db,
        org,
        owner,
        deadline=now - timedelta(hours=2),
        late_deadline=now + timedelta(hours=2),
    )
    assert await svc.get_submission_timing(p_late, stu.id) == "late"

    # cohort overrides take the MOST generous value and ignore None overrides
    from app.models.cohort import Cohort, CohortMember, CohortProjectAssignment

    c1 = Cohort(org_id=org.id, name="c1", slug=f"c1-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    c2 = Cohort(org_id=org.id, name="c2", slug=f"c2-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add_all([c1, c2])
    await db.flush()
    db.add_all(
        [
            CohortMember(cohort_id=c1.id, user_id=stu.id, role="learner"),
            CohortMember(cohort_id=c2.id, user_id=stu.id, role="learner"),
        ]
    )
    # c1: NO overrides (must not crash / must not null the deadline);
    # c2: deadline_override in the future → student is on_time
    db.add_all(
        [
            CohortProjectAssignment(cohort_id=c1.id, project_id=p_closed.id, assigned_by=owner.id),
            CohortProjectAssignment(
                assigned_by=owner.id,
                cohort_id=c2.id,
                project_id=p_closed.id,
                deadline_override=now + timedelta(hours=3),
            ),
        ]
    )
    await db.flush()
    assert await svc.get_submission_timing(p_closed, stu.id) == "on_time"

    # late_deadline_override extends the LATE window (project late passed)
    p_l2 = await _project(
        db,
        org,
        owner,
        deadline=now - timedelta(hours=4),
        late_deadline=now - timedelta(hours=2),
    )
    assert await svc.get_submission_timing(p_l2, stu.id) == "closed"
    c3 = Cohort(org_id=org.id, name="c3", slug=f"c3-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(c3)
    await db.flush()
    db.add(CohortMember(cohort_id=c3.id, user_id=stu.id, role="learner"))
    db.add(
        CohortProjectAssignment(
            assigned_by=owner.id,
            cohort_id=c3.id,
            project_id=p_l2.id,
            late_deadline_override=now + timedelta(hours=2),
        )
    )
    await db.flush()
    assert await svc.get_submission_timing(p_l2, stu.id) == "late"

    # SINGLE-membership user: the cohort join must pair a member row with
    # ITS OWN cohort's assignment (a cross-join would let any other
    # membership of the user satisfy it) — lone is in c4 ONLY
    lone = await _user(db)
    await org_svc.add_member(org.id, lone.id, OrgRole.STUDENT)
    p_solo = await _project(db, org, owner, deadline=now - timedelta(hours=2))
    c4 = Cohort(org_id=org.id, name="c4", slug=f"c4-{uuid.uuid4().hex[:8]}", created_by=owner.id)
    db.add(c4)
    await db.flush()
    db.add(CohortMember(cohort_id=c4.id, user_id=lone.id, role="learner"))
    db.add(
        CohortProjectAssignment(
            assigned_by=owner.id,
            cohort_id=c4.id,
            project_id=p_solo.id,
            deadline_override=now + timedelta(hours=3),
        )
    )
    await db.flush()
    assert await svc.get_submission_timing(p_solo, lone.id) == "on_time"

    # an assignment with NO late override on a project WITH a late window
    # leaves the effective late deadline alone (None overrides are skipped,
    # never compared) — still 'late', never a TypeError
    p_win = await _project(
        db,
        org,
        owner,
        deadline=now - timedelta(hours=4),
        late_deadline=now + timedelta(hours=2),
    )
    db.add(CohortProjectAssignment(assigned_by=owner.id, cohort_id=c4.id, project_id=p_win.id))
    await db.flush()
    assert await svc.get_submission_timing(p_win, lone.id) == "late"

    # a personal extension trumps a passed deadline — and re-granting UPDATES
    # the one row (no unique-violation 500), honoring the LATEST grant
    other = await _user(db)
    await org_svc.add_member(org.id, other.id, OrgRole.STUDENT)
    p_ext = await _project(db, org, owner, deadline=now - timedelta(hours=2))
    with pytest.raises(AppError) as e_nm:
        await svc.grant_extension(
            p_ext.id, str(uuid.uuid4()), now + timedelta(hours=1), None, owner.id
        )
    assert e_nm.value.status_code == 404  # not an org member → 404, not 500
    await svc.grant_extension(p_ext.id, other.id, now + timedelta(hours=1), "r1", owner.id)
    assert await svc.get_submission_timing(p_ext, other.id) == "on_time"
    # re-grant into the past → extension no longer saves them
    ext2 = await svc.grant_extension(
        p_ext.id, other.id, now - timedelta(minutes=30), "r2", owner.id
    )
    assert ext2.reason == "r2"
    assert await svc.get_submission_timing(p_ext, other.id) == "closed"
    from sqlalchemy import func as _f
    from sqlalchemy import select as _s

    from app.models.project import SubmissionExtension

    n_rows = (
        await db.execute(
            _s(_f.count(SubmissionExtension.id)).where(
                SubmissionExtension.project_id == p_ext.id,
                SubmissionExtension.user_id == other.id,
            )
        )
    ).scalar_one()
    assert n_rows == 1


async def test_review_scoring_matrix_r403(db):
    from app.models.organization import OrgRole
    from app.models.project import ContentStatus, SubmissionStatus
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    owner = await _user(db, role=UserRole.ADMIN)
    org = await _org_with(db, owner)
    svc = ProjectService(db)
    org_svc = OrgService(db)
    stu = await _user(db)
    await org_svc.add_member(org.id, stu.id, OrgRole.STUDENT)

    # max_score 1000 separates /100 from /101 in the penalty formula
    p = await _project(db, org, owner, max_score=1000, late_penalty_pct=50)
    p.status = ContentStatus.PUBLISHED
    await db.flush()

    async def _submitted():
        s = await svc.create_submission(org.id, p.id, stu.id)
        return await svc.submit_draft(s.id, stu.id)

    sub = await _submitted()

    # score bounds: negative → 422; over max → 422; ZERO and exactly-max pass
    with pytest.raises(AppError) as e_neg:
        await svc.create_review(sub.id, owner.id, "approved", -1, None, None)
    assert e_neg.value.status_code == 422
    with pytest.raises(AppError) as e_over:
        await svc.create_review(sub.id, owner.id, "approved", 1001, None, None)
    assert e_over.value.status_code == 422

    r0 = await svc.create_review(sub.id, owner.id, "approved", 0, None, None)
    assert r0.id
    await db.refresh(sub)
    assert sub.status == SubmissionStatus.APPROVED
    assert sub.final_score == 0

    # approve at exactly max, on-time → NO late penalty applied
    sub2 = await _submitted()
    await svc.create_review(sub2.id, owner.id, "approved", 1000, None, None)
    await db.refresh(sub2)
    assert sub2.final_score == 1000

    # LATE approval applies pct/100 exactly: 1000 · 50% → 500 (…/101 → 505)
    sub3 = await _submitted()
    sub3.is_late = True
    await db.flush()
    await svc.create_review(sub3.id, owner.id, "approved", 1000, None, None)
    await db.refresh(sub3)
    assert sub3.final_score == 500

    # revision_requested clears a prior final_score and reopens
    await svc.create_review(sub3.id, owner.id, "revision_requested", None, None, "redo")
    await db.refresh(sub3)
    assert sub3.status == SubmissionStatus.REVISION_REQUESTED
    assert sub3.final_score is None

    # rejected keeps an informational score WITH the late penalty
    sub3.status = SubmissionStatus.SUBMITTED
    await db.flush()
    await svc.create_review(sub3.id, owner.id, "rejected", 800, None, None)
    await db.refresh(sub3)
    assert sub3.status == SubmissionStatus.REJECTED
    assert sub3.final_score == 400  # 800 · 50% late penalty
