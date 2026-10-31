"""Risk Classification service (ADR-017 Part B).

Configurable scoring policies, versioned assessments, separation-of-duty
enforcement, and tier denormalization to the system record.
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import AppError
from app.trustplane.models.inventory import AISystem, RiskTier
from app.trustplane.models.risk import (
    DEFAULT_DIMENSIONS,
    DEFAULT_TIER_THRESHOLDS,
    AssessmentStatus,
    RiskAssessment,
    RiskScoringPolicy,
)
from app.trustplane.services.audit import record_trust_audit
from app.trustplane.services.inventory import SystemNotFoundError

# ── Errors ───────────────────────────────────────────────────────────


class AssessmentNotFoundError(AppError):
    def __init__(self):
        super().__init__("ASSESSMENT_NOT_FOUND", "Risk assessment not found", 404)


class SelfApprovalForbiddenError(AppError):
    def __init__(self):
        super().__init__(
            "SELF_APPROVAL_FORBIDDEN",
            "Author cannot approve their own risk assessment",
            422,
        )


class AssessmentAlreadyDecidedError(AppError):
    def __init__(self, status: str):
        super().__init__(
            "ASSESSMENT_ALREADY_DECIDED",
            f"Assessment is already '{status}' and cannot be reviewed again",
            409,
        )


class AssessmentIncompleteError(AppError):
    def __init__(self, missing: list[str]):
        super().__init__(
            "ASSESSMENT_INCOMPLETE",
            f"Missing dimension scores: {', '.join(missing)}",
            422,
            details=[{"field": k, "message": "Score required"} for k in missing],
        )


class OverrideJustificationRequiredError(AppError):
    def __init__(self):
        super().__init__(
            "OVERRIDE_JUSTIFICATION_REQUIRED",
            "Justification is required when overriding the computed risk tier",
            422,
        )


class PolicyNotFoundError(AppError):
    def __init__(self):
        super().__init__("POLICY_NOT_FOUND", "Risk scoring policy not found", 404)


class AssessmentNotSubmittedError(AppError):
    def __init__(self):
        super().__init__(
            "ASSESSMENT_NOT_SUBMITTED",
            "Assessment must be in 'submitted' status to be reviewed",
            422,
        )


class RejectionJustificationRequiredError(AppError):
    def __init__(self):
        super().__init__(
            "REJECTION_JUSTIFICATION_REQUIRED",
            "Justification is required when rejecting a risk assessment",
            422,
        )


# ── Scoring policy ───────────────────────────────────────────────────


async def get_or_create_default_policy(
    db: AsyncSession, org_id: str
) -> RiskScoringPolicy:
    """Return the active policy for org, falling back to platform default."""
    # 1. Org-specific active policy
    result = await db.execute(
        select(RiskScoringPolicy).where(
            RiskScoringPolicy.org_id == org_id,
            RiskScoringPolicy.is_active.is_(True),
        )
    )
    policy = result.scalar_one_or_none()
    if policy is not None:
        return policy

    # 2. Platform default (org_id IS NULL)
    result = await db.execute(
        select(RiskScoringPolicy).where(
            RiskScoringPolicy.org_id.is_(None),
            RiskScoringPolicy.is_active.is_(True),
        )
    )
    policy = result.scalar_one_or_none()
    if policy is not None:
        return policy

    # 3. Create platform default on first call
    policy = RiskScoringPolicy(
        org_id=None,
        name="Platform Default Risk Policy",
        version=1,
        is_active=True,
        dimensions=DEFAULT_DIMENSIONS,
        tier_thresholds=DEFAULT_TIER_THRESHOLDS,
    )
    db.add(policy)
    await db.flush()
    return policy


async def create_policy(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    name: str,
    dimensions: list,
    tier_thresholds: dict,
) -> RiskScoringPolicy:
    # Deactivate current active policy for org
    result = await db.execute(
        select(RiskScoringPolicy).where(
            RiskScoringPolicy.org_id == org_id,
            RiskScoringPolicy.is_active.is_(True),
        )
    )
    old_policy = result.scalar_one_or_none()
    if old_policy is not None:
        old_policy.is_active = False
        await record_trust_audit(
            db,
            org_id=org_id,
            actor_user_id=user_id,
            actor_type="user",
            action="policy.deactivated",
            target_type="risk_scoring_policy",
            target_id=old_policy.id,
        )

    new_version = (old_policy.version + 1) if old_policy else 1
    policy = RiskScoringPolicy(
        org_id=org_id,
        name=name,
        version=new_version,
        is_active=True,
        dimensions=dimensions,
        tier_thresholds=tier_thresholds,
        created_by=user_id,
    )
    db.add(policy)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="policy.created",
        target_type="risk_scoring_policy",
        target_id=policy.id,
        after={"name": name, "version": new_version},
    )
    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="policy.activated",
        target_type="risk_scoring_policy",
        target_id=policy.id,
    )
    return policy


async def list_policies(
    db: AsyncSession,
    org_id: str,
) -> list[RiskScoringPolicy]:
    result = await db.execute(
        select(RiskScoringPolicy)
        .where(
            (RiskScoringPolicy.org_id == org_id) | (RiskScoringPolicy.org_id.is_(None))
        )
        .order_by(RiskScoringPolicy.created_at.desc())
    )
    return list(result.scalars().all())


# ── Risk assessment lifecycle ────────────────────────────────────────


def _compute_weighted_score(
    dimension_scores: dict, dimensions: list
) -> Decimal:
    """Weighted average of dimension scores."""
    total_weight = Decimal(0)
    weighted_sum = Decimal(0)
    for dim in dimensions:
        key = dim["key"]
        weight = Decimal(str(dim["weight"]))
        score = Decimal(str(dimension_scores.get(key, 0)))
        weighted_sum += score * weight
        total_weight += weight
    if total_weight == 0:
        return Decimal(0)
    return (weighted_sum / total_weight).quantize(Decimal("0.01"))


def _derive_tier(score: Decimal, thresholds: dict) -> RiskTier:
    """Derive risk tier from weighted score using threshold config."""
    for tier in (RiskTier.MINIMAL, RiskTier.LOW, RiskTier.MEDIUM, RiskTier.HIGH):
        max_score = thresholds.get(tier.value, {}).get("max_score")
        if max_score is not None and score <= Decimal(str(max_score)):
            return tier
    return RiskTier.CRITICAL


async def create_assessment(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    user_id: str,
    *,
    dimension_scores: dict,
    policy_id: str | None = None,
) -> RiskAssessment:
    # Validate system exists in org
    result = await db.execute(
        select(AISystem).where(AISystem.id == system_id, AISystem.org_id == org_id)
    )
    if result.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    # Resolve policy
    if policy_id:
        policy = await db.get(RiskScoringPolicy, policy_id)
        if policy is None:
            raise PolicyNotFoundError()
    else:
        policy = await get_or_create_default_policy(db, org_id)

    # Auto-increment version
    max_ver = await db.execute(
        select(func.coalesce(func.max(RiskAssessment.version), 0)).where(
            RiskAssessment.system_id == system_id
        )
    )
    next_version = (max_ver.scalar() or 0) + 1

    assessment = RiskAssessment(
        system_id=system_id,
        policy_id=policy.id,
        version=next_version,
        status=AssessmentStatus.DRAFT,
        dimension_scores=dimension_scores,
        assessed_by=user_id,
    )
    db.add(assessment)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="assessment.created",
        target_type="risk_assessment",
        target_id=assessment.id,
        after={"system_id": system_id, "version": next_version},
    )
    return assessment


async def submit_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    user_id: str,
) -> RiskAssessment:
    assessment = await _get_assessment(db, assessment_id, org_id)
    if assessment.status != AssessmentStatus.DRAFT:
        raise AssessmentAlreadyDecidedError(assessment.status.value)

    # Load policy for scoring
    policy = await db.get(RiskScoringPolicy, assessment.policy_id)
    if policy is None:
        raise PolicyNotFoundError()

    # Validate all dimension scores are present
    required_keys = [d["key"] for d in policy.dimensions]
    missing = [k for k in required_keys if k not in assessment.dimension_scores]
    if missing:
        raise AssessmentIncompleteError(missing)

    # Compute score and tier
    assessment.weighted_score = _compute_weighted_score(
        assessment.dimension_scores, policy.dimensions
    )
    assessment.computed_tier = _derive_tier(assessment.weighted_score, policy.tier_thresholds)
    assessment.effective_tier = assessment.override_tier or assessment.computed_tier
    assessment.status = AssessmentStatus.SUBMITTED
    assessment.submitted_at = datetime.now(UTC)
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="assessment.submitted",
        target_type="risk_assessment",
        target_id=assessment_id,
        after={
            "weighted_score": str(assessment.weighted_score),
            "computed_tier": assessment.computed_tier.value,
            "effective_tier": assessment.effective_tier.value,
        },
    )
    return assessment


async def approve_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    reviewer_id: str,
) -> RiskAssessment:
    assessment = await _get_assessment(db, assessment_id, org_id)
    if assessment.status != AssessmentStatus.SUBMITTED:
        raise AssessmentNotSubmittedError()

    # Separation of duty
    if assessment.assessed_by == reviewer_id:
        raise SelfApprovalForbiddenError()

    # Supersede previous approved assessment for same system
    result = await db.execute(
        select(RiskAssessment).where(
            RiskAssessment.system_id == assessment.system_id,
            RiskAssessment.status == AssessmentStatus.APPROVED,
        )
    )
    for old in result.scalars().all():
        old.status = AssessmentStatus.SUPERSEDED
        await record_trust_audit(
            db,
            org_id=org_id,
            actor_user_id=reviewer_id,
            actor_type="user",
            action="assessment.superseded",
            target_type="risk_assessment",
            target_id=old.id,
        )

    assessment.status = AssessmentStatus.APPROVED
    assessment.reviewed_by = reviewer_id
    assessment.reviewed_at = datetime.now(UTC)

    # Denormalize effective_tier → system.risk_tier
    system = await db.get(AISystem, assessment.system_id)
    if system is not None:
        system.risk_tier = assessment.effective_tier

    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=reviewer_id,
        actor_type="user",
        action="assessment.approved",
        target_type="risk_assessment",
        target_id=assessment_id,
        after={"effective_tier": assessment.effective_tier.value if assessment.effective_tier else None},
    )
    return assessment


async def reject_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    reviewer_id: str,
    justification: str,
) -> RiskAssessment:
    if not justification or not justification.strip():
        raise RejectionJustificationRequiredError()

    assessment = await _get_assessment(db, assessment_id, org_id)
    if assessment.status != AssessmentStatus.SUBMITTED:
        raise AssessmentNotSubmittedError()

    if assessment.assessed_by == reviewer_id:
        raise SelfApprovalForbiddenError()

    assessment.status = AssessmentStatus.REJECTED
    assessment.reviewed_by = reviewer_id
    assessment.reviewed_at = datetime.now(UTC)
    assessment.justification = justification
    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=reviewer_id,
        actor_type="user",
        action="assessment.rejected",
        target_type="risk_assessment",
        target_id=assessment_id,
        reason=justification,
    )
    return assessment


async def override_tier(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
    user_id: str,
    new_tier: str,
    justification: str,
) -> RiskAssessment:
    if not justification or not justification.strip():
        raise OverrideJustificationRequiredError()

    assessment = await _get_assessment(db, assessment_id, org_id)
    old_tier = assessment.override_tier.value if assessment.override_tier else None
    assessment.override_tier = RiskTier(new_tier)
    assessment.effective_tier = assessment.override_tier
    assessment.justification = justification

    # If approved, also update the system's denormalized tier
    if assessment.status == AssessmentStatus.APPROVED:
        system = await db.get(AISystem, assessment.system_id)
        if system is not None:
            system.risk_tier = assessment.effective_tier

    await db.flush()

    await record_trust_audit(
        db,
        org_id=org_id,
        actor_user_id=user_id,
        actor_type="user",
        action="assessment.tier_overridden",
        target_type="risk_assessment",
        target_id=assessment_id,
        before={"override_tier": old_tier},
        after={"override_tier": new_tier, "effective_tier": new_tier},
        reason=justification,
    )
    return assessment


async def get_assessment(
    db: AsyncSession,
    assessment_id: str,
    org_id: str,
) -> RiskAssessment:
    return await _get_assessment(db, assessment_id, org_id)


async def list_assessments(
    db: AsyncSession,
    system_id: str,
    org_id: str,
    *,
    status: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[RiskAssessment], int]:
    # Validate system belongs to org
    sys_result = await db.execute(
        select(AISystem.id).where(AISystem.id == system_id, AISystem.org_id == org_id)
    )
    if sys_result.scalar_one_or_none() is None:
        raise SystemNotFoundError()

    base = select(RiskAssessment).where(RiskAssessment.system_id == system_id)
    count_base = (
        select(func.count())
        .select_from(RiskAssessment)
        .where(RiskAssessment.system_id == system_id)
    )

    if status:
        base = base.where(RiskAssessment.status == status)
        count_base = count_base.where(RiskAssessment.status == status)

    total = (await db.execute(count_base)).scalar() or 0
    result = await db.execute(
        base.order_by(RiskAssessment.version.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return list(result.scalars().all()), total


# ── Helpers ──────────────────────────────────────────────────────────


async def _get_assessment(
    db: AsyncSession, assessment_id: str, org_id: str
) -> RiskAssessment:
    """Load assessment, verify its system belongs to the given org."""
    assessment = await db.get(RiskAssessment, assessment_id)
    if assessment is None:
        raise AssessmentNotFoundError()

    # Check system belongs to org
    sys_result = await db.execute(
        select(AISystem.id).where(
            AISystem.id == assessment.system_id, AISystem.org_id == org_id
        )
    )
    if sys_result.scalar_one_or_none() is None:
        raise AssessmentNotFoundError()

    return assessment
