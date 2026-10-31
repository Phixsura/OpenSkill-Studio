"""Runtime Guardrails & Action Boundaries service (ADR-017 Part F).

Server-side enforcement that cannot be disabled by model output, prompts,
or extension manifests. Records policy version and reason for blocked
or escalated actions.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.guardrails import (
    ActionBoundary,
    EvalVerdict,
    GuardrailEvaluation,
    GuardrailPolicy,
    GuardrailStatus,
    GuardrailType,
)
from app.trustplane.services.audit import record_trust_audit

# ── Errors ───────────────────────────────────────────────────────────


class GuardrailNotFoundError(AppError):
    def __init__(self):
        super().__init__("GUARDRAIL_NOT_FOUND", "Guardrail policy not found", 404)


class BoundaryNotFoundError(AppError):
    def __init__(self):
        super().__init__("BOUNDARY_NOT_FOUND", "Action boundary not found", 404)


class BoundaryExceededError(AppError):
    def __init__(self, name: str, limit: int, current: int):
        super().__init__(
            "BOUNDARY_EXCEEDED",
            f"Action boundary '{name}' exceeded: {current}/{limit}",
            429,
        )


# ── Guardrail Policy CRUD ───────────────────────────────────────────


async def create_guardrail(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    name: str,
    guardrail_type: str,
    config: dict,
    system_id: str | None = None,
    description: str | None = None,
    is_blocking: bool = True,
    priority: int = 100,
) -> GuardrailPolicy:
    policy = GuardrailPolicy(
        org_id=org_id,
        system_id=system_id,
        name=name,
        description=description,
        guardrail_type=GuardrailType(guardrail_type),
        status=GuardrailStatus.DRAFT,
        config=config,
        is_blocking=is_blocking,
        priority=priority,
        created_by=user_id,
    )
    db.add(policy)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="guardrail.created",
        target_type="guardrail_policy",
        target_id=policy.id,
        after={"name": name, "guardrail_type": guardrail_type},
    )
    return policy


async def get_guardrail(db: AsyncSession, guardrail_id: str, org_id: str) -> GuardrailPolicy:
    result = await db.execute(
        select(GuardrailPolicy).where(
            GuardrailPolicy.id == guardrail_id, GuardrailPolicy.org_id == org_id
        )
    )
    policy = result.scalar_one_or_none()
    if policy is None:
        raise GuardrailNotFoundError()
    return policy


async def list_guardrails(
    db: AsyncSession,
    org_id: str,
    *,
    guardrail_type: str | None = None,
    system_id: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[GuardrailPolicy], int]:
    base = select(GuardrailPolicy).where(GuardrailPolicy.org_id == org_id)
    count_base = (
        select(func.count()).select_from(GuardrailPolicy).where(GuardrailPolicy.org_id == org_id)
    )

    if guardrail_type:
        base = base.where(GuardrailPolicy.guardrail_type == guardrail_type)
        count_base = count_base.where(GuardrailPolicy.guardrail_type == guardrail_type)
    if system_id:
        base = base.where(GuardrailPolicy.system_id == system_id)
        count_base = count_base.where(GuardrailPolicy.system_id == system_id)
    if status:
        base = base.where(GuardrailPolicy.status == status)
        count_base = count_base.where(GuardrailPolicy.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(GuardrailPolicy.priority, GuardrailPolicy.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def activate_guardrail(
    db: AsyncSession,
    guardrail_id: str,
    org_id: str,
    user_id: str,
) -> GuardrailPolicy:
    policy = await get_guardrail(db, guardrail_id, org_id)
    old = policy.status.value
    policy.status = GuardrailStatus.ACTIVE
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="guardrail.activated",
        target_type="guardrail_policy",
        target_id=guardrail_id,
        before={"status": old},
        after={"status": "active"},
    )
    return policy


async def disable_guardrail(
    db: AsyncSession,
    guardrail_id: str,
    org_id: str,
    user_id: str,
) -> GuardrailPolicy:
    policy = await get_guardrail(db, guardrail_id, org_id)
    old = policy.status.value
    policy.status = GuardrailStatus.DISABLED
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="guardrail.disabled",
        target_type="guardrail_policy",
        target_id=guardrail_id,
        before={"status": old},
        after={"status": "disabled"},
    )
    return policy


# ── Guardrail Evaluation ────────────────────────────────────────────


async def record_evaluation(
    db: AsyncSession,
    org_id: str,
    *,
    policy_id: str,
    policy_version: int,
    verdict: str,
    run_id: str | None = None,
    step_id: str | None = None,
    system_id: str | None = None,
    reason: str | None = None,
    input_summary: dict | None = None,
    output_summary: dict | None = None,
) -> GuardrailEvaluation:
    evaluation = GuardrailEvaluation(
        org_id=org_id,
        policy_id=policy_id,
        policy_version=policy_version,
        run_id=run_id,
        step_id=step_id,
        system_id=system_id,
        verdict=EvalVerdict(verdict),
        reason=reason,
        input_summary=input_summary,
        output_summary=output_summary,
    )
    db.add(evaluation)
    await db.flush()
    return evaluation


async def list_evaluations(
    db: AsyncSession,
    org_id: str,
    *,
    policy_id: str | None = None,
    verdict: str | None = None,
    run_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[GuardrailEvaluation], int]:
    base = select(GuardrailEvaluation).where(GuardrailEvaluation.org_id == org_id)
    count_base = (
        select(func.count())
        .select_from(GuardrailEvaluation)
        .where(GuardrailEvaluation.org_id == org_id)
    )

    if policy_id:
        base = base.where(GuardrailEvaluation.policy_id == policy_id)
        count_base = count_base.where(GuardrailEvaluation.policy_id == policy_id)
    if verdict:
        base = base.where(GuardrailEvaluation.verdict == verdict)
        count_base = count_base.where(GuardrailEvaluation.verdict == verdict)
    if run_id:
        base = base.where(GuardrailEvaluation.run_id == run_id)
        count_base = count_base.where(GuardrailEvaluation.run_id == run_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(GuardrailEvaluation.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Action Boundaries ────────────────────────────────────────────────


async def create_boundary(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    name: str,
    boundary_type: str,
    limit_value: int,
    limit_period: str | None = None,
    system_id: str | None = None,
) -> ActionBoundary:
    boundary = ActionBoundary(
        org_id=org_id,
        system_id=system_id,
        name=name,
        boundary_type=boundary_type,
        limit_value=limit_value,
        limit_period=limit_period,
        created_by=user_id,
    )
    db.add(boundary)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="boundary.created",
        target_type="action_boundary",
        target_id=boundary.id,
        after={"name": name, "boundary_type": boundary_type, "limit_value": limit_value},
    )
    return boundary


async def check_boundary(
    db: AsyncSession,
    boundary_id: str,
    org_id: str,
) -> ActionBoundary:
    """Check if a boundary has been exceeded. Raises BoundaryExceededError if so."""
    result = await db.execute(
        select(ActionBoundary).where(
            ActionBoundary.id == boundary_id,
            ActionBoundary.org_id == org_id,
            ActionBoundary.is_active.is_(True),
        )
    )
    boundary = result.scalar_one_or_none()
    if boundary is None:
        raise BoundaryNotFoundError()

    if boundary.current_usage >= boundary.limit_value:
        raise BoundaryExceededError(boundary.name, boundary.limit_value, boundary.current_usage)

    return boundary


async def increment_boundary(
    db: AsyncSession,
    boundary_id: str,
    org_id: str,
    amount: int = 1,
) -> ActionBoundary:
    """Increment usage counter for a boundary."""
    result = await db.execute(
        select(ActionBoundary).where(
            ActionBoundary.id == boundary_id, ActionBoundary.org_id == org_id
        )
    )
    boundary = result.scalar_one_or_none()
    if boundary is None:
        raise BoundaryNotFoundError()

    boundary.current_usage += amount
    await db.flush()
    return boundary


async def list_boundaries(
    db: AsyncSession,
    org_id: str,
    *,
    system_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[ActionBoundary], int]:
    base = select(ActionBoundary).where(ActionBoundary.org_id == org_id)
    count_base = (
        select(func.count()).select_from(ActionBoundary).where(ActionBoundary.org_id == org_id)
    )

    if system_id:
        base = base.where(ActionBoundary.system_id == system_id)
        count_base = count_base.where(ActionBoundary.system_id == system_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(ActionBoundary.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total
