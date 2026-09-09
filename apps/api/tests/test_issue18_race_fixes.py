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
