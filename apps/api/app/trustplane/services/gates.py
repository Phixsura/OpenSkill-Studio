"""Release & Install Gates service (ADR-017 Part D).

Assurance profiles define reusable check templates. Gate results record
each evaluation — a passing aggregate score never overrides a hard
policy violation (blocking check).
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.gates import (
    AssuranceProfile,
    CheckType,
    GateCheck,
    GateOutcome,
    GateResult,
    GateTrigger,
    ProfileStatus,
)
from app.trustplane.services.audit import record_trust_audit

# ── Errors ───────────────────────────────────────────────────────────


class ProfileNotFoundError(AppError):
    def __init__(self):
        super().__init__("PROFILE_NOT_FOUND", "Assurance profile not found", 404)


class GateResultNotFoundError(AppError):
    def __init__(self):
        super().__init__("GATE_RESULT_NOT_FOUND", "Gate result not found", 404)


class CheckNotFoundError(AppError):
    def __init__(self):
        super().__init__("CHECK_NOT_FOUND", "Gate check not found", 404)


class GateBlockedError(AppError):
    def __init__(self, failed_checks: list[str]):
        super().__init__(
            "GATE_BLOCKED",
            f"Gate blocked by failing checks: {', '.join(failed_checks)}",
            422,
        )


# ── Assurance Profile CRUD ───────────────────────────────────────────


async def create_profile(
    db: AsyncSession,
    org_id: str | None,
    user_id: str,
    *,
    name: str,
    trigger: str,
    description: str | None = None,
) -> AssuranceProfile:
    profile = AssuranceProfile(
        org_id=org_id,
        name=name,
        description=description,
        trigger=GateTrigger(trigger),
        status=ProfileStatus.DRAFT,
        created_by=user_id,
    )
    db.add(profile)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id or "__platform__",
        actor_user_id=user_id,
        actor_type="user",
        action="profile.created",
        target_type="assurance_profile",
        target_id=profile.id,
        after={"name": name, "trigger": trigger},
    )
    return profile


async def get_profile(db: AsyncSession, profile_id: str, org_id: str) -> AssuranceProfile:
    result = await db.execute(
        select(AssuranceProfile).where(
            AssuranceProfile.id == profile_id,
            (AssuranceProfile.org_id == org_id) | (AssuranceProfile.org_id.is_(None)),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise ProfileNotFoundError()
    return profile


async def list_profiles(
    db: AsyncSession,
    org_id: str,
    *,
    trigger: str | None = None,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[AssuranceProfile], int]:
    base = select(AssuranceProfile).where(
        (AssuranceProfile.org_id == org_id) | (AssuranceProfile.org_id.is_(None))
    )
    count_base = select(func.count()).select_from(AssuranceProfile).where(
        (AssuranceProfile.org_id == org_id) | (AssuranceProfile.org_id.is_(None))
    )

    if trigger:
        base = base.where(AssuranceProfile.trigger == trigger)
        count_base = count_base.where(AssuranceProfile.trigger == trigger)
    if status:
        base = base.where(AssuranceProfile.status == status)
        count_base = count_base.where(AssuranceProfile.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(AssuranceProfile.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


async def activate_profile(
    db: AsyncSession,
    profile_id: str,
    org_id: str,
    user_id: str,
) -> AssuranceProfile:
    profile = await get_profile(db, profile_id, org_id)
    profile.status = ProfileStatus.ACTIVE
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="profile.activated",
        target_type="assurance_profile",
        target_id=profile_id,
    )
    return profile


# ── Gate Checks ──────────────────────────────────────────────────────


async def add_check(
    db: AsyncSession,
    profile_id: str,
    org_id: str,
    user_id: str,
    *,
    name: str,
    check_type: str,
    is_blocking: bool = True,
    config: dict | None = None,
    description: str | None = None,
) -> GateCheck:
    await get_profile(db, profile_id, org_id)

    # Auto-ordinal
    max_ord = await db.execute(
        select(func.coalesce(func.max(GateCheck.ordinal), -1)).where(
            GateCheck.profile_id == profile_id
        )
    )
    next_ord = (max_ord.scalar() or 0) + 1

    check = GateCheck(
        profile_id=profile_id,
        name=name,
        description=description,
        check_type=CheckType(check_type),
        is_blocking=is_blocking,
        config=config or {},
        ordinal=next_ord,
    )
    db.add(check)
    await db.flush()
    return check


async def list_checks(
    db: AsyncSession,
    profile_id: str,
    org_id: str,
) -> list[GateCheck]:
    await get_profile(db, profile_id, org_id)
    result = await db.execute(
        select(GateCheck)
        .where(GateCheck.profile_id == profile_id)
        .order_by(GateCheck.ordinal)
    )
    return list(result.scalars().all())


# ── Gate Evaluation ──────────────────────────────────────────────────


async def evaluate_gate(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    profile_id: str,
    target_type: str,
    target_id: str,
    target_version: str | None = None,
    check_results: list[dict],
) -> GateResult:
    """Record a gate evaluation. Each check_result is:
    {"check_id": str, "outcome": "passed"|"failed"|"skipped", "detail": str|None}
    A single blocking failure → overall FAILED.
    """
    await get_profile(db, profile_id, org_id)  # validates existence & org access
    checks = await list_checks(db, profile_id, org_id)
    check_map = {c.id: c for c in checks}

    failed_blocking = []
    for cr in check_results:
        check = check_map.get(cr.get("check_id", ""))
        if check and check.is_blocking and cr.get("outcome") == "failed":
            failed_blocking.append(check.name)

    overall = GateOutcome.PASSED if not failed_blocking else GateOutcome.FAILED

    gate_result = GateResult(
        org_id=org_id,
        profile_id=profile_id,
        target_type=target_type,
        target_id=target_id,
        target_version=target_version,
        outcome=overall,
        check_results=check_results,
        evaluated_by=user_id,
    )
    db.add(gate_result)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="gate.evaluated",
        target_type="gate_result",
        target_id=gate_result.id,
        after={
            "profile_id": profile_id,
            "target": f"{target_type}:{target_id}",
            "outcome": overall.value,
        },
    )
    return gate_result


async def override_gate(
    db: AsyncSession,
    result_id: str,
    org_id: str,
    user_id: str,
    justification: str,
) -> GateResult:
    """Override a FAILED gate result with justification."""
    result = await db.execute(
        select(GateResult).where(GateResult.id == result_id, GateResult.org_id == org_id)
    )
    gate_result = result.scalar_one_or_none()
    if gate_result is None:
        raise GateResultNotFoundError()

    gate_result.outcome = GateOutcome.OVERRIDDEN
    gate_result.override_justification = justification
    gate_result.override_by = user_id
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="gate.overridden",
        target_type="gate_result",
        target_id=result_id,
        after={"outcome": "overridden"},
        reason=justification,
    )
    return gate_result


async def list_gate_results(
    db: AsyncSession,
    org_id: str,
    *,
    target_type: str | None = None,
    target_id: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[GateResult], int]:
    base = select(GateResult).where(GateResult.org_id == org_id)
    count_base = select(func.count()).select_from(GateResult).where(GateResult.org_id == org_id)

    if target_type:
        base = base.where(GateResult.target_type == target_type)
        count_base = count_base.where(GateResult.target_type == target_type)
    if target_id:
        base = base.where(GateResult.target_id == target_id)
        count_base = count_base.where(GateResult.target_id == target_id)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(GateResult.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total
