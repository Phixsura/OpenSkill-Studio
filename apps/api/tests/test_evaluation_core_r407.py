"""R407: evaluation service core mutation hardening (pass-2 left 25 live).

Documented EQUIVALENT mutants (adjudicated, no test possible):
- L1200 ``split("```json", 1) -> maxsplit 2`` and L1202/L1204 maxsplit bumps:
  ``parts[1]`` is identical for any maxsplit >= 1 (the inner ``split("```")``
  truncates at the first closing fence regardless).
- L1201 ``len(parts) > 1 -> >=``: guarded by ``"```json" in response``, the
  split always yields >= 2 parts, so both comparisons agree.
- L1205 ``len(parts) > 1 -> >=``: same guard with ``"```" in response``.
"""

import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.llm import LLMResponse
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.evaluation import EvalStatus, EvaluationTask
from app.models.user import User, UserRole, UserStatus
from app.services.evaluation import EvaluationService


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


GOOD = LLMResponse(
    content=(
        '{"scores":[{"criterion":"Q","score":80,"max_score":100,"feedback":"ok"}],'
        '"overall_feedback":"fine","strengths":[],"improvements":[]}'
    ),
    input_tokens=500,
    output_tokens=200,
    model="claude-sonnet-5",
    provider="anthropic",
)


async def _user(db):
    u = User(
        email=f"r407-{uuid.uuid4().hex[:10]}@test.com",
        password_hash=hash_password("Test123!"),
        display_name="R407",
        role=UserRole.ADMIN,
        status=UserStatus.ACTIVE,
    )
    db.add(u)
    await db.flush()
    return u


async def _org_sub(db, user, *, enabled=True):
    """org + tenant + published project + submitted submission."""
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    org = await OrgService(db).create(
        name=f"R407 {uuid.uuid4().hex[:6]}",
        slug=f"r407-{uuid.uuid4().hex[:10]}",
        description=None,
        created_by=user.id,
    )
    svc = EvaluationService(db)
    if enabled:
        await svc.update_eval_settings(org.id, {"enabled": True})
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "R407P",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        user.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, user.id)
    await proj_svc.submit_draft(sub.id, user.id)
    await db.flush()
    return org, sub


def _mock_llm(response=GOOD):
    mock_llm = AsyncMock()
    mock_llm.complete = AsyncMock(return_value=response)
    p = patch("app.services.evaluation.create_llm_client")
    m = p.start()
    m.return_value = mock_llm
    return p


async def test_trigger_bogus_and_cross_org_submission_404_r407(db):
    user = await _user(db)
    org, sub = await _org_sub(db, user)
    org2, sub2 = await _org_sub(db, user)
    svc = EvaluationService(db)

    with pytest.raises(AppError) as e_bogus:
        await svc.trigger_evaluation(org.id, str(uuid.uuid4()), "submission_review")
    assert e_bogus.value.status_code == 404
    assert e_bogus.value.code == "SUBMISSION_NOT_FOUND"

    # cross-org id: exists, but belongs to org2 → SAME 404, never a run
    with pytest.raises(AppError) as e_cross:
        await svc.trigger_evaluation(org.id, sub2.id, "submission_review")
    assert e_cross.value.status_code == 404


async def test_prepay_zero_estimate_requires_balance_r407(db):
    """L284: projected == 0 (avg completed cost rounds to zero minor) must
    take the require_available arm → INSUFFICIENT_CREDIT 402, not a
    zero-amount reservation (VALIDATION_ERROR 422)."""
    from app.controlplane.models.tenant import TenantAccount

    user = await _user(db)
    org, sub = await _org_sub(db, user)
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.metadata_ = {"credit_enforcement": True}
    await db.flush()

    # a COMPLETED task with cost 0.001 USD → avg 0.001 → 0.1 minor → 0
    db.add(
        EvaluationTask(
            org_id=org.id,
            submission_id=sub.id,
            type="submission_review",
            status=EvalStatus.COMPLETED,
            config={},
            cost_usd=Decimal("0.001"),
        )
    )
    await db.flush()
    svc = EvaluationService(db)
    assert await svc._estimate_eval_cost_minor(org.id) == 0

    llm = _mock_llm()
    try:
        with pytest.raises(AppError) as exc:
            await svc.trigger_evaluation(org.id, sub.id, "submission_review")
        assert exc.value.code == "INSUFFICIENT_CREDIT"
        assert exc.value.status_code == 402

        # …and a FAILED task retried under the same zero estimate hits the
        # SAME arm (L635) — and the prepay gate cannot be skipped (L634)
        failed = EvaluationTask(
            org_id=org.id,
            submission_id=sub.id,
            type="submission_review",
            status=EvalStatus.FAILED,
            config={},
        )
        db.add(failed)
        await db.flush()
        with pytest.raises(AppError) as exc2:
            await svc.retry_task(failed.id)
        assert exc2.value.code == "INSUFFICIENT_CREDIT"
        assert exc2.value.status_code == 402
    finally:
        llm.stop()


async def test_retry_and_cancel_claims_r407(db):
    user = await _user(db)
    org, sub = await _org_sub(db, user)
    svc = EvaluationService(db)

    # decoys FIRST: one FAILED and one PENDING task — an inverted claim
    # predicate would match these instead of the target
    decoy_failed = EvaluationTask(
        org_id=org.id,
        submission_id=sub.id,
        type="submission_review",
        status=EvalStatus.FAILED,
        config={},
    )
    decoy_pending = EvaluationTask(
        org_id=org.id,
        submission_id=sub.id,
        type="submission_review",
        status=EvalStatus.PENDING,
        config={},
    )
    completed = EvaluationTask(
        org_id=org.id,
        submission_id=sub.id,
        type="submission_review",
        status=EvalStatus.COMPLETED,
        config={},
        cost_usd=Decimal("0.05"),
    )
    db.add_all([decoy_failed, decoy_pending, completed])
    await db.flush()

    # retry of a COMPLETED task → 422 exactly (the FAILED decoy must not be
    # claimed in its place)
    with pytest.raises(AppError) as e_retry:
        await svc.retry_task(completed.id)
    assert e_retry.value.status_code == 422
    await db.refresh(decoy_failed)
    assert decoy_failed.status == EvalStatus.FAILED, "decoy must be untouched"

    # cancel of a COMPLETED task → 422 exactly (the PENDING decoy untouched)
    with pytest.raises(AppError) as e_cancel:
        await svc.cancel_task(completed.id)
    assert e_cancel.value.status_code == 422
    await db.refresh(decoy_pending)
    assert decoy_pending.status == EvalStatus.PENDING, "decoy must be untouched"

    # cancel of the PENDING task → CANCELLED
    cancelled = await svc.cancel_task(decoy_pending.id)
    assert cancelled.status == EvalStatus.CANCELLED

    # retry of the FAILED task claims it and re-executes (mocked LLM)
    llm = _mock_llm()
    try:
        retried = await svc.retry_task(decoy_failed.id)
        assert retried.status == EvalStatus.COMPLETED
    finally:
        llm.stop()


async def test_estimate_scopes_and_fx_r407(db):
    """L735: the estimate averages COMPLETED tasks only; L757: a non-USD
    tenant converts via FX before going to minor units."""
    from app.controlplane.models.pricing import FxRate
    from app.controlplane.models.tenant import TenantAccount

    user = await _user(db)
    org, sub = await _org_sub(db, user)
    svc = EvaluationService(db)

    db.add_all(
        [
            EvaluationTask(
                org_id=org.id,
                submission_id=sub.id,
                type="submission_review",
                status=EvalStatus.COMPLETED,
                config={},
                cost_usd=Decimal("7.77"),
            ),
            EvaluationTask(
                org_id=org.id,
                submission_id=sub.id,
                type="submission_review",
                status=EvalStatus.FAILED,
                config={},
                cost_usd=Decimal("99.99"),
            ),
        ]
    )
    await db.flush()
    assert await svc._estimate_eval_cost_minor(org.id) == 777

    # switch the tenant to BND with a pinned USD→BND rate of 2
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.currency = "BND"
    db.add(
        FxRate(
            base_currency="USD",
            quote_currency="BND",
            rate=Decimal("2"),
            effective_from=datetime.now(UTC) - timedelta(days=1),
        )
    )
    await db.flush()
    assert await svc._estimate_eval_cost_minor(org.id) == 1554  # 7.77 × 2 × 100


async def test_check_budget_legacy_and_cp_codes_r407(db):
    from app.models.evaluation import EvalUsageMonthly
    from app.models.organization import Organization
    from app.services.evaluation import _current_month_utc

    user = await _user(db)
    org, sub = await _org_sub(db, user)
    svc = EvaluationService(db)
    await svc.update_eval_settings(org.id, {"monthly_budget_usd": 50})

    # spend EXACTLY at the budget in the CURRENT month → blocked (>= not >),
    # and the month filter must match the current month (an old row would
    # read as $0 spent)
    db.add(
        EvalUsageMonthly(
            org_id=org.id,
            month=_current_month_utc(),
            total_tasks=1,
            total_cost_usd=Decimal("50"),
        )
    )
    await db.flush()
    assert await svc.check_budget(org.id) is False

    # under budget → True
    row = (
        await db.execute(select(EvalUsageMonthly).where(EvalUsageMonthly.org_id == org.id))
    ).scalar_one()
    row.total_cost_usd = Decimal("49.99")
    await db.flush()
    assert await svc.check_budget(org.id) is True

    # CP budget outcomes: BUDGET_EXCEEDED → False; TENANT_NOT_FOUND → True
    with patch(
        "app.controlplane.services.budgets.check",
        AsyncMock(side_effect=AppError("BUDGET_EXCEEDED", "over", 402)),
    ):
        assert await svc.check_budget(org.id) is False
    with patch(
        "app.controlplane.services.budgets.check",
        AsyncMock(side_effect=AppError("TENANT_NOT_FOUND", "gone", 404)),
    ):
        assert await svc.check_budget(org.id) is True

    # settings update on a bogus org → 404 exactly
    with pytest.raises(AppError) as e_org:
        await svc.update_eval_settings(str(uuid.uuid4()), {"enabled": True})
    assert e_org.value.status_code == 404
    assert isinstance(await db.get(Organization, org.id), Organization)


def test_parse_fences_and_untrusted_rubric_r407():
    rubric = [{"criterion": "Q", "max_score": 10}]

    # ```json fence with TRAILING prose: only the fenced block is parsed
    fenced = (
        'preamble\n```json\n{"scores":[{"criterion":"Q","score":5}],'
        '"overall_feedback":"f"}\n```\nAs you can see, great work.'
    )
    out = EvaluationService._parse_evaluation_response(fenced, rubric)
    assert out["total_score"] == 5
    assert out["max_score"] == 10

    # UNCLOSED plain fence: everything after the fence is the payload
    unclosed = '```\n{"scores":[{"criterion":"Q","score":4}],"overall_feedback":"f"}'
    out2 = EvaluationService._parse_evaluation_response(unclosed, rubric)
    assert out2["total_score"] == 4

    # hallucinated rubric types never crash or count: a STRING max_score is
    # treated as 0 (not a TypeError in min()), a BOOL max_score likewise
    out3 = EvaluationService._parse_evaluation_response(
        '{"scores":[{"criterion":"S","score":5},{"criterion":"B","score":5}],'
        '"overall_feedback":"f"}',
        [{"criterion": "S", "max_score": "10"}, {"criterion": "B", "max_score": True}],
    )
    assert out3["total_score"] == 0
    assert out3["max_score"] == 0
