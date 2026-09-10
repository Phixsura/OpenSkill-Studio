"""Issue-18 stale-read-write debt: two-session interleaving regression tests.

The R70 class (Python gate on a stale status read → unguarded ORM write) was
fixed across the flagged issue-18 services with guarded conditional UPDATEs /
FOR UPDATE re-reads. Each test drives a REAL interleave: session A claims and
holds its transaction open; session B races the same transition, blocks on the
row (or advisory) lock, and must resolve to the documented conflict error —
never a double transition, a lost update, or a 500.
"""

import asyncio
from datetime import UTC, datetime

import pytest
from sqlalchemy import select, update
from ulid import ULID

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus

pytestmark = pytest.mark.asyncio


async def _mk_user(db) -> User:
    user = User(
        email=f"i18-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="I18 Race",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_org(db, user):
    from app.services.organization import OrgService

    return await OrgService(db).create(
        name=f"I18 {ULID()}",
        slug=f"i18-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )


async def test_cancel_blocks_behind_executor_claim():
    """cancel_task raced _execute_evaluation's PENDING→PROCESSING flip and
    stamped CANCELLED over a task that actually ran. With the guarded
    transitions, a cancel that loses the claim race 422s."""
    from app.core.database import engine
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask
    from app.services.evaluation import EvaluationService

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            org = await _mk_org(setup, user)
            task = EvaluationTask(
                org_id=org.id, type=EvalType.SUBMISSION_REVIEW, status=EvalStatus.PENDING, config={}
            )
            setup.add(task)
            await setup.commit()
            task_id = task.id

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        outcomes: list[str] = []
        try:
            # A = the executor's claim (PENDING→PROCESSING), held uncommitted.
            claim = await sa.execute(
                update(EvaluationTask)
                .where(EvaluationTask.id == task_id, EvaluationTask.status == EvalStatus.PENDING)
                .values(status=EvalStatus.PROCESSING, started_at=datetime.now(UTC))
            )
            assert claim.rowcount == 1

            async def b_cancel():
                try:
                    await EvaluationService(sb).cancel_task(task_id)
                    await sb.commit()
                    outcomes.append("cancelled")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)

            b = asyncio.create_task(b_cancel())
            await asyncio.sleep(0.3)  # B blocked on the row lock
            await sa.commit()
            await b
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["INVALID_STATE"], outcomes
        async with AsyncSessionLocal() as s:
            t = await s.get(EvaluationTask, task_id)
            assert t.status == EvalStatus.PROCESSING, (
                f"cancel overwrote the executor claim: {t.status}"
            )
    finally:
        await engine.dispose()


async def test_execute_claim_skips_cancelled_task():
    """_execute_evaluation must abort (no LLM call, no PROCESSING overwrite)
    when the task was cancelled before its claim."""
    from app.core.database import engine
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask
    from app.services.evaluation import EvaluationService

    try:
        async with AsyncSessionLocal() as db:
            user = await _mk_user(db)
            org = await _mk_org(db, user)
            task = EvaluationTask(
                org_id=org.id,
                type=EvalType.SUBMISSION_REVIEW,
                status=EvalStatus.CANCELLED,
                config={},
            )
            db.add(task)
            await db.flush()
            await EvaluationService(db)._execute_evaluation(task)
            assert task.status == EvalStatus.CANCELLED, (
                "executor overwrote a cancelled task with PROCESSING"
            )
            await db.rollback()
    finally:
        await engine.dispose()


async def test_retry_loser_gets_422_not_double_run():
    """Two concurrent retries of a FAILED task both reserved credit and both
    ran the paid LLM call. The loser now blocks on the claim and 422s."""
    from app.core.database import engine
    from app.models.evaluation import EvalStatus, EvalType, EvaluationTask
    from app.services.evaluation import EvaluationService

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            org = await _mk_org(setup, user)
            task = EvaluationTask(
                org_id=org.id, type=EvalType.SUBMISSION_REVIEW, status=EvalStatus.FAILED, config={}
            )
            setup.add(task)
            await setup.commit()
            task_id = task.id

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        outcomes: list[str] = []
        try:
            # A = the winning retry's claim (FAILED→PENDING), held open.
            claim = await sa.execute(
                update(EvaluationTask)
                .where(EvaluationTask.id == task_id, EvaluationTask.status == EvalStatus.FAILED)
                .values(status=EvalStatus.PENDING, error=None)
            )
            assert claim.rowcount == 1

            async def b_retry():
                try:
                    await EvaluationService(sb).retry_task(task_id)
                    await sb.commit()
                    outcomes.append("retried")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)

            b = asyncio.create_task(b_retry())
            await asyncio.sleep(0.3)
            await sa.commit()
            await b
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["INVALID_STATE"], outcomes
    finally:
        await engine.dispose()


async def test_double_convert_creates_one_project():
    """Two concurrent convert_to_project calls on one DRAFT brief created TWO
    projects. The DRAFT→ACTIVE claim serializes them; the loser 422s."""
    from app.core.database import engine
    from app.models.client_brief import BriefStatus, ClientBrief
    from app.models.project import Project
    from app.services.client_brief import ClientBriefService

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            org = await _mk_org(setup, user)
            brief = ClientBrief(
                org_id=org.id,
                title="Race brief",
                slug=f"race-{str(ULID()).lower()}",
                client_name="Acme",
                project_type="brand_visuals",
                objective="obj",
                status=BriefStatus.DRAFT,
                created_by=user.id,
            )
            setup.add(brief)
            await setup.commit()
            brief_id, org_id, user_id = brief.id, org.id, user.id

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        outcomes: list[str] = []
        try:
            # A converts fully (claim + project creation), holds uncommitted.
            await ClientBriefService(sa).convert_to_project(brief_id, org_id, user_id)

            async def b_convert():
                try:
                    await ClientBriefService(sb).convert_to_project(brief_id, org_id, user_id)
                    await sb.commit()
                    outcomes.append("converted")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)

            b = asyncio.create_task(b_convert())
            await asyncio.sleep(0.3)  # B blocked on the brief-row claim
            await sa.commit()
            await b
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["INVALID_STATE"], outcomes
        async with AsyncSessionLocal() as s:
            projects = (
                (await s.execute(select(Project).where(Project.client_brief_id == brief_id)))
                .scalars()
                .all()
            )
            assert len(projects) == 1, f"{len(projects)} projects off one brief"
    finally:
        await engine.dispose()


async def test_concurrent_add_member_409_not_500():
    """Two concurrent add_member calls for the same (org, user) both passed the
    existence pre-check; the loser died on uq_org_member as an unhandled 500.
    SAVEPOINT isolation turns it into the documented AlreadyMemberError 409."""
    from app.core.database import engine
    from app.models.organization import OrgRole
    from app.services.organization import OrgService

    try:
        async with AsyncSessionLocal() as setup:
            owner = await _mk_user(setup)
            member_user = await _mk_user(setup)
            org = await _mk_org(setup, owner)
            await setup.commit()
            org_id, member_id = org.id, member_user.id

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        outcomes: list[str] = []
        try:
            # A inserts and HOLDS (existence pre-check in B sees nothing; B
            # then blocks on the tenant seat advisory lock A already holds).
            await OrgService(sa).add_member(org_id, member_id, OrgRole.STUDENT)

            async def b_add():
                try:
                    await OrgService(sb).add_member(org_id, member_id, OrgRole.STUDENT)
                    await sb.commit()
                    outcomes.append("added")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)
                except Exception as exc:  # noqa: BLE001 — the pre-fix 500 path
                    await sb.rollback()
                    outcomes.append(type(exc).__name__)

            b = asyncio.create_task(b_add())
            await asyncio.sleep(0.3)
            await sa.commit()
            await b
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["ALREADY_MEMBER"], outcomes
    finally:
        await engine.dispose()


async def test_cohort_slug_collision_retry_no_session_poison():
    """R160 (schemathesis): non-ASCII cohort names collapse to the same slug;
    the FIRST retry flush was un-SAVEPOINT'd, so a second collision (concurrent
    create or suffix race) poisoned the session → PendingRollbackError 500 on
    the next statement. The savepoint-retry loop must yield unique slugs and
    never poison the session — 5 same-collapsing-name creates all succeed."""
    from app.core.database import engine
    from app.models.cohort import Cohort
    from app.services.cohort import CohortService

    try:
        async with AsyncSessionLocal() as s:
            user = await _mk_user(s)
            org = await _mk_org(s, user)
            await s.commit()
            org_id = org.id

        # All these names collapse to the same base slug via _generate_slug.
        names = ["team alpha", "team!alpha", "team@@@alpha", "TEAM  ALPHA", "team.alpha"]  # all → base slug "team-alpha"
        async with AsyncSessionLocal() as s:
            svc = CohortService(s)
            made = []
            for nm in names:
                cohort = await svc.create_cohort(org_id, name=nm, description=None,
                                                 created_by=user.id)
                made.append(cohort.id)
            await s.commit()
            # a normal op AFTER the retries must work (session not poisoned)
            await svc.create_cohort(org_id, name="normal cohort", description=None,
                                            created_by=user.id)
            await s.commit()
        async with AsyncSessionLocal() as s:
            rows = (
                (await s.execute(select(Cohort).where(Cohort.org_id == org_id)))
                .scalars().all()
            )
            slugs = [r.slug for r in rows]
            assert len(rows) == len(names) + 1, f"{len(rows)} cohorts (expected {len(names)+1})"
            assert len(set(slugs)) == len(slugs), f"duplicate slugs: {slugs}"
    finally:
        await engine.dispose()


async def test_double_start_assessment_allocates_once():
    """R173: two concurrent start_assessment calls on one SETUP round both
    passed the phase gate and both allocated — the allocation is RANDOM, so
    the (round, submission, reviewer) unique index only stops identical
    pairs: the net effect was doubled reviewer workload or a 500 at commit.
    The round-row lock serializes them; the loser re-reads ASSESSMENT → 422."""
    from app.core.database import engine
    from app.models.project import PeerAssessment
    from app.services.peer_review import PeerReviewService

    try:
        async with AsyncSessionLocal() as setup:
            instructor = await _mk_user(setup)
            org = await _mk_org(setup, instructor)
            learners = [await _mk_user(setup) for _ in range(4)]
            project_id, round_id = await _peer_round(setup, org, instructor, learners)
            await setup.commit()

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        outcomes: list[str] = []
        try:
            # A: allocate and HOLD the transaction open (lock on the round row)
            rnd_a, count_a = await PeerReviewService(sa).start_assessment(round_id, org.id)
            assert count_a > 0

            async def b_start():
                try:
                    await PeerReviewService(sb).start_assessment(round_id, org.id)
                    await sb.commit()
                    outcomes.append("allocated")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)

            b = asyncio.create_task(b_start())
            await asyncio.sleep(0.3)
            assert not outcomes, "B must be blocked on the round lock, not finished"
            await sa.commit()
            await b
        finally:
            await sa.close()
            await sb.close()

        assert outcomes == ["INVALID_PHASE"], outcomes
        async with AsyncSessionLocal() as s:
            n = (
                await s.execute(
                    select(PeerAssessment).where(PeerAssessment.round_id == round_id)
                )
            ).scalars().all()
            assert len(n) == count_a, f"expected single allocation ({count_a}), got {len(n)}"
    finally:
        await engine.dispose()


async def _peer_round(db, org, instructor, learners):
    """Project + one SUBMITTED submission per learner + a SETUP round."""
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.models.project import ItemType, SubmissionItem
    from app.services.peer_review import PeerReviewService
    from app.services.project import ProjectService

    psvc = ProjectService(db)
    project = await psvc.create_project(
        org_id=org.id,
        title=f"I18 Peer {ULID()}",
        slug=None,
        description="d",
        instructions="i",
        difficulty="beginner",
        max_score=100,
        rubric=[{"criterion": "Q", "max_score": 100}],
        deadline=None,
        late_deadline=None,
        late_penalty_pct=0,
        max_submissions=0,
        skill_ids=None,
        created_by=instructor.id,
    )
    d = await psvc.create_deliverable(project.id, "Work", None, "text", True, {}, 0)
    for learner in learners:
        db.add(
            OrgMember(
                org_id=org.id, user_id=learner.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE
            )
        )
        await db.flush()
        sub = await psvc.create_submission(org.id, project.id, learner.id)
        db.add(
            SubmissionItem(
                submission_id=sub.id, deliverable_id=d.id, type=ItemType.TEXT, content="w"
            )
        )
        await db.flush()
        await psvc.submit_draft(sub.id, learner.id)
    rnd = await PeerReviewService(db).create_round(
        org.id, project.id, instructor.id, name="R173", num_reviews=2
    )
    return project.id, rnd.id


async def test_concurrent_first_profile_touch_no_500():
    """R174: get_or_create_profile is check-then-insert on BOTH the PK (same
    user's parallel first requests) and the username unique index (two users
    with the same display name). Each bare-flush race was a 500. The loser
    must recover: same-user → return the winner's row; same-username →
    retry with a random suffix."""
    from app.core.database import engine
    from app.services.portfolio import PortfolioService

    try:
        async with AsyncSessionLocal() as setup:
            # Two distinct users with an IDENTICAL display name → identical
            # generated username base.
            u1 = await _mk_user(setup)
            u2 = await _mk_user(setup)
            clash = f"Race Clash {str(ULID()).lower()}"
            u1.display_name = clash
            u2.display_name = clash
            await setup.commit()
            u1_id, u2_id = u1.id, u2.id

        # ── shape (b): username unique-index race across two users ──
        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            pa = await PortfolioService(sa).get_or_create_profile(u1_id)  # holds insert
            username_a = pa.username

            async def b_create():
                profile = await PortfolioService(sb).get_or_create_profile(u2_id)
                name = profile.username
                await sb.commit()
                return name

            b = asyncio.create_task(b_create())
            await asyncio.sleep(0.3)
            await sa.commit()
            username_b = await b
        finally:
            await sa.close()
            await sb.close()
        assert username_b != username_a, "loser must have retried with a suffix"
        assert username_b.startswith(username_a[:30])

        # ── shape (a): same-user PK race ──
        async with AsyncSessionLocal() as setup:
            u3 = await _mk_user(setup)
            await setup.commit()
            u3_id = u3.id
        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            pa = await PortfolioService(sa).get_or_create_profile(u3_id)

            async def b_same_user():
                profile = await PortfolioService(sb).get_or_create_profile(u3_id)
                name = profile.username
                await sb.commit()
                return name

            b = asyncio.create_task(b_same_user())
            await asyncio.sleep(0.3)
            await sa.commit()
            username_b3 = await b
        finally:
            await sa.close()
            await sb.close()
        assert username_b3 == pa.username, "loser must return the winner's profile"
    finally:
        await engine.dispose()


async def test_concurrent_set_override_no_500():
    """R187: set_override is check-then-insert on uq_cp_ent_override — two
    concurrent sets of the same (tenant, key) both passed the existence
    pre-check and the loser died on the unique index as an unhandled 500
    (an admin double-clicking Save races itself). The loser must now update
    the winner's row instead."""
    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.controlplane.services.audit import Actor
    from app.controlplane.services.plans import set_override
    from app.controlplane.services.tenants import create_tenant
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await create_tenant(
                setup,
                name=f"I18 Ovr {ULID()}",
                slug=f"i18ovr-{str(ULID()).lower()}",
                actor=Actor(user_id=user.id, type="tenant"),
                owner_user_id=user.id,
            )
            await setup.commit()
            tenant_id = tenant.id
            actor = Actor(user_id=user.id, type="platform")

        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            ta = await sa.get(
                __import__("app.controlplane.models.tenant", fromlist=["TenantAccount"]).TenantAccount,
                tenant_id,
            )
            tb = await sb.get(
                __import__("app.controlplane.models.tenant", fromlist=["TenantAccount"]).TenantAccount,
                tenant_id,
            )
            # A inserts and HOLDS (uncommitted) — B's insert will block on the
            # unique index until A commits, then hit IntegrityError.
            await set_override(
                sa, ta.id, "max_organizations", value=5, enforcement="hard",
                expires_at=None, reason="A", actor=actor,
            )

            async def b_set():
                await set_override(
                    sb, tb.id, "max_organizations", value=9, enforcement="hard",
                    expires_at=None, reason="B", actor=actor,
                )
                await sb.commit()

            b = asyncio.create_task(b_set())
            await asyncio.sleep(0.3)
            await sa.commit()
            await b  # must not raise
        finally:
            await sa.close()
            await sb.close()

        async with AsyncSessionLocal() as s:
            rows = (
                (
                    await s.execute(
                        select(TenantEntitlementOverride).where(
                            TenantEntitlementOverride.tenant_id == tenant_id,
                            TenantEntitlementOverride.key == "max_organizations",
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, "must converge to one override row"
            assert rows[0].value == {"v": 9}, "loser's update must win (last-writer)"
    finally:
        await engine.dispose()


async def test_concurrent_admin_demotions_never_reach_zero_admins():
    """R199: the last-admin check was an UNLOCKED count-then-write — two
    concurrent demotions of the two remaining admins both counted 2 (>1),
    both proceeded, and ZERO active admins remained (platform lockout).
    Drive the REAL endpoint concurrently: exactly one demotion must 422."""
    from httpx import ASGITransport, AsyncClient

    from app.core.database import engine
    from app.core.security import create_access_token
    from app.main import app

    try:
        # The platform may already hold admins from other suites — demote them
        # so OUR pair are the only two active admins (restored afterwards).
        async with AsyncSessionLocal() as setup:
            prior = (
                (
                    await setup.execute(
                        select(User).where(
                            User.role == UserRole.ADMIN, User.status == UserStatus.ACTIVE
                        )
                    )
                )
                .scalars()
                .all()
            )
            prior_ids = [u.id for u in prior]
            for u in prior:
                u.role = UserRole.STUDENT
            a1 = await _mk_user(setup)
            a2 = await _mk_user(setup)
            a1.role = UserRole.ADMIN
            a2.role = UserRole.ADMIN
            await setup.commit()
            a1_id, a2_id = a1.id, a2.id
            t1 = create_access_token(a1_id, a1.email, "admin")
            t2 = create_access_token(a2_id, a2.email, "admin")

        from contextlib import asynccontextmanager

        orig = app.router.lifespan_context

        @asynccontextmanager
        async def _noop(a):
            yield

        app.router.lifespan_context = _noop
        try:
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:

                async def demote(token, target):
                    return await c.put(
                        f"/api/v1/admin/users/{target}/role",
                        json={"role": "student"},
                        headers={"Authorization": f"Bearer {token}"},
                    )

                r1, r2 = await asyncio.gather(demote(t1, a2_id), demote(t2, a1_id))
                codes = sorted([r1.status_code, r2.status_code])
                assert codes == [200, 422], f"expected one success one refusal, got {codes}"
        finally:
            app.router.lifespan_context = orig

        async with AsyncSessionLocal() as s:
            remaining = (
                (
                    await s.execute(
                        select(User.id).where(
                            User.id.in_([a1_id, a2_id]),
                            User.role == UserRole.ADMIN,
                            User.status == UserStatus.ACTIVE,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(remaining) == 1, f"exactly one admin must survive, got {len(remaining)}"
            # Restore the platform admins demoted for isolation.
            for pid in prior_ids:
                u = await s.get(User, pid)
                if u is not None:
                    u.role = UserRole.ADMIN
            await s.commit()
    finally:
        await engine.dispose()


async def test_concurrent_extension_grants_no_500():
    """R200: grant_extension's one-per-(project,user) pre-check raced a
    concurrent grant — the loser died on uq_extension_project_user as an
    unhandled 500. The savepointed insert now falls back to updating the
    winner's row (last-writer, matching the update branch)."""
    from datetime import UTC, datetime, timedelta

    from app.core.database import engine
    from app.models.organization import MemberStatus, OrgMember, OrgRole
    from app.models.project import SubmissionExtension
    from app.services.project import ProjectService

    try:
        async with AsyncSessionLocal() as setup:
            instructor = await _mk_user(setup)
            org = await _mk_org(setup, instructor)
            student = await _mk_user(setup)
            setup.add(
                OrgMember(
                    org_id=org.id, user_id=student.id,
                    role=OrgRole.STUDENT, status=MemberStatus.ACTIVE,
                )
            )
            project = await ProjectService(setup).create_project(
                org_id=org.id, title=f"Ext {ULID()}", slug=None, description="d",
                instructions="i", difficulty="beginner", max_score=100,
                rubric=[{"criterion": "Q", "max_score": 100}], deadline=None,
                late_deadline=None, late_penalty_pct=0, max_submissions=0,
                skill_ids=None, created_by=instructor.id,
            )
            await setup.commit()
            pid, sid, iid = project.id, student.id, instructor.id

        d1 = datetime.now(UTC) + timedelta(days=3)
        d2 = datetime.now(UTC) + timedelta(days=7)
        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            # A inserts and holds (uncommitted)
            await ProjectService(sa).grant_extension(pid, sid, d1, "A", iid)

            async def b_grant():
                await ProjectService(sb).grant_extension(pid, sid, d2, "B", iid)
                await sb.commit()

            b = asyncio.create_task(b_grant())
            await asyncio.sleep(0.3)
            await sa.commit()
            await b  # must not raise
        finally:
            await sa.close()
            await sb.close()

        async with AsyncSessionLocal() as s:
            rows = (
                (
                    await s.execute(
                        select(SubmissionExtension).where(
                            SubmissionExtension.project_id == pid,
                            SubmissionExtension.user_id == sid,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, "must converge to one extension row"
            assert rows[0].reason == "B", "loser's update must win"
    finally:
        await engine.dispose()
