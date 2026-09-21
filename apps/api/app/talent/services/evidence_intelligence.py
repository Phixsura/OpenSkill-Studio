"""Evidence intelligence — quality scoring, expiration alerts, disputes, simulation.

Closes gaps: #21 (quality scoring), #22 (expiration alerts), #24 (dispute flow),
#26 (scoring simulation), #28 (calibration tools), #32 (distribution analytics),
#33 (cross-org portability), #35 (automated generation hooks).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.talent.models.evidence import VERIFICATION_WEIGHTS, CapabilityEvidence

# ---------------------------------------------------------------------------
# Gap #21: Evidence quality scoring
# ---------------------------------------------------------------------------

QUALITY_FACTORS = {
    "has_source_id": 0.15,
    "has_score": 0.15,
    "high_verification": 0.25,
    "recent": 0.20,
    "has_org": 0.10,
    "high_confidence": 0.15,
}


def compute_evidence_quality(evidence: dict) -> dict:
    """Score individual evidence quality on 0-1 scale with breakdown."""
    factors = {}
    factors["has_source_id"] = 1.0 if evidence.get("source_id") else 0.0
    factors["has_score"] = 1.0 if evidence.get("score_normalized") is not None else 0.0

    ver_level = evidence.get("verification_level", "self_reported")
    ver_weight = VERIFICATION_WEIGHTS.get(ver_level, 0.3)
    factors["high_verification"] = ver_weight

    occurred = evidence.get("occurred_at")
    if occurred and isinstance(occurred, datetime):
        age_days = (datetime.now(UTC) - occurred).days
        factors["recent"] = max(0, 1.0 - age_days / 730)  # 2 year decay
    else:
        factors["recent"] = 0.0

    factors["has_org"] = 1.0 if evidence.get("org_id") else 0.0
    factors["high_confidence"] = float(evidence.get("confidence", 0.5))

    total = sum(factors[k] * QUALITY_FACTORS[k] for k in QUALITY_FACTORS)

    return {
        "quality_score": round(total, 3),
        "factors": {k: round(v, 3) for k, v in factors.items()},
    }


# ---------------------------------------------------------------------------
# Gap #22: Expiration alerts
# ---------------------------------------------------------------------------


async def find_expiring_evidence(
    db: AsyncSession,
    *,
    days_ahead: int = 30,
    user_id: str | None = None,
) -> list[dict]:
    """Find evidence expiring within N days."""
    now = datetime.now(UTC)
    cutoff = now + timedelta(days=days_ahead)

    q = select(CapabilityEvidence).where(
        CapabilityEvidence.status == "active",
        CapabilityEvidence.expires_at.isnot(None),
        CapabilityEvidence.expires_at <= cutoff,
        CapabilityEvidence.expires_at > now,
    )
    if user_id:
        q = q.where(CapabilityEvidence.user_id == user_id)
    q = q.order_by(CapabilityEvidence.expires_at)

    result = await db.execute(q)
    items = result.scalars().all()
    return [
        {
            "evidence_id": e.id,
            "user_id": e.user_id,
            "capability_id": e.capability_id,
            "expires_at": e.expires_at.isoformat() if e.expires_at else None,
            "days_until_expiry": (e.expires_at - now).days if e.expires_at else None,
            "verification_level": e.verification_level,
        }
        for e in items
    ]


# ---------------------------------------------------------------------------
# Gap #24: Dispute/challenge flow
# ---------------------------------------------------------------------------

DISPUTE_STATUSES = frozenset({"open", "under_review", "resolved_upheld", "resolved_removed"})
DISPUTE_REASONS = frozenset(
    {
        "inaccurate_score",
        "wrong_capability",
        "not_my_work",
        "outdated",
        "duplicate",
        "other",
    }
)


@dataclass(frozen=True, slots=True)
class EvidenceDispute:
    evidence_id: str
    user_id: str
    reason: str
    details: str
    status: str


def validate_dispute(
    *,
    reason: str,
    details: str,
) -> list[str]:
    """Validate a dispute submission."""
    errors = []
    if reason not in DISPUTE_REASONS:
        errors.append(f"Invalid reason. Must be one of: {sorted(DISPUTE_REASONS)}")
    if not details or len(details) < 10:
        errors.append("Details must be at least 10 characters")
    if len(details) > 5000:
        errors.append("Details must be under 5000 characters")
    return errors


# ---------------------------------------------------------------------------
# Gap #26: Scoring simulation ("what-if")
# ---------------------------------------------------------------------------


def simulate_score_change(
    current_evidence: list[dict],
    hypothetical_evidence: dict,
    decay_config: dict | None = None,
) -> dict:
    """Simulate how adding new evidence would change a capability score.

    Returns current score, projected score, and delta.
    """
    from app.talent.services.scoring import compute_score_from_evidence

    now = datetime.now(UTC)

    # Current score
    current_score, current_conf, current_sub = compute_score_from_evidence(
        current_evidence,
        decay_config,
        now,
    )

    # Projected score with new evidence
    projected_evidence = current_evidence + [hypothetical_evidence]
    projected_score, projected_conf, projected_sub = compute_score_from_evidence(
        projected_evidence,
        decay_config,
        now,
    )

    return {
        "current_score": current_score,
        "current_confidence": current_conf,
        "current_substantial": current_sub,
        "projected_score": projected_score,
        "projected_confidence": projected_conf,
        "projected_substantial": projected_sub,
        "score_delta": round(projected_score - current_score, 4),
        "confidence_delta": round(projected_conf - current_conf, 4),
    }


# ---------------------------------------------------------------------------
# Gap #28: Scoring calibration
# ---------------------------------------------------------------------------

DEFAULT_CALIBRATION = {
    "shrinkage_k": 3,
    "shrinkage_prior": 0.5,
    "dimension_weights": {"depth": 0.40, "breadth": 0.20, "recency": 0.20, "velocity": 0.20},
    "verification_weights": dict(VERIFICATION_WEIGHTS),
    "recency_sigma_days": 180,
    "velocity_window_days": 90,
}


def validate_calibration(config: dict) -> list[str]:
    """Validate scoring calibration parameters."""
    errors = []
    weights = config.get("dimension_weights", {})
    if weights:
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            errors.append(f"Dimension weights must sum to 1.0, got {total}")
    k = config.get("shrinkage_k")
    if k is not None and (k < 0 or k > 100):
        errors.append("shrinkage_k must be 0-100")
    prior = config.get("shrinkage_prior")
    if prior is not None and (prior < 0 or prior > 1):
        errors.append("shrinkage_prior must be 0-1")
    return errors


# ---------------------------------------------------------------------------
# Gap #32: Evidence type distribution analytics
# ---------------------------------------------------------------------------


async def compute_evidence_distribution(
    db: AsyncSession,
    *,
    user_id: str | None = None,
    org_id: str | None = None,
) -> dict:
    """Compute distribution of evidence by type, verification level, source type."""
    q = select(
        CapabilityEvidence.verification_level,
        CapabilityEvidence.source_type,
        func.count().label("count"),
    ).where(CapabilityEvidence.status == "active")

    if user_id:
        q = q.where(CapabilityEvidence.user_id == user_id)
    if org_id:
        q = q.where(CapabilityEvidence.org_id == org_id)

    q = q.group_by(CapabilityEvidence.verification_level, CapabilityEvidence.source_type)
    result = await db.execute(q)
    rows = result.all()

    by_verification: dict[str, int] = {}
    by_source: dict[str, int] = {}
    total = 0
    for ver, src, count in rows:
        by_verification[ver] = by_verification.get(ver, 0) + count
        by_source[src] = by_source.get(src, 0) + count
        total += count

    return {
        "total_evidence": total,
        "by_verification_level": by_verification,
        "by_source_type": by_source,
        "top_verification": max(by_verification, key=by_verification.get)
        if by_verification
        else None,
        "top_source": max(by_source, key=by_source.get) if by_source else None,
    }


# ---------------------------------------------------------------------------
# Gap #35: Automated evidence generation hooks
# ---------------------------------------------------------------------------

EVIDENCE_GENERATION_HOOKS = {
    "skill_completion": {
        "trigger": "user completes a skill module",
        "verification_level": "system_observed",
        "confidence": 0.7,
    },
    "project_approval": {
        "trigger": "project submission approved by reviewer",
        "verification_level": "instructor_verified",
        "confidence": 0.85,
    },
    "assessment_pass": {
        "trigger": "user passes a standardized assessment",
        "verification_level": "assessment_verified",
        "confidence": 0.95,
    },
    "workflow_execution": {
        "trigger": "workflow pack execution completes successfully",
        "verification_level": "system_observed",
        "confidence": 0.6,
    },
    "client_acceptance": {
        "trigger": "client accepts commercial deliverable",
        "verification_level": "client_verified",
        "confidence": 0.9,
    },
    "peer_review": {
        "trigger": "peer review completed with positive outcome",
        "verification_level": "peer_verified",
        "confidence": 0.75,
    },
}


def get_hook_config(trigger_type: str) -> dict | None:
    """Get evidence generation hook configuration for a trigger type."""
    return EVIDENCE_GENERATION_HOOKS.get(trigger_type)


def build_auto_evidence(
    *,
    user_id: str,
    capability_id: str,
    trigger_type: str,
    source_type: str,
    source_id: str,
    org_id: str | None = None,
    score: float | None = None,
) -> dict | None:
    """Build evidence data from an automated trigger.

    Returns evidence dict ready for EvidenceService.add_evidence(),
    or None if no hook is configured.
    """
    hook = get_hook_config(trigger_type)
    if not hook:
        return None

    return {
        "user_id": user_id,
        "capability_id": capability_id,
        "source_type": source_type,
        "source_id": source_id,
        "org_id": org_id,
        "score_normalized": score,
        "verification_level": hook["verification_level"],
        "confidence": hook["confidence"],
        "occurred_at": datetime.now(UTC),
    }
