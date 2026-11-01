"""The ONLY trust-plane import surface for product code.

Product services/routers call these functions; they must never import
`app.trustplane.models` / `app.trustplane.services` directly, so the
trust domain can evolve without rippling through the product layer.

Functions are thin delegations — the real logic lives in
app/trustplane/services/*. Each is filled in by its owning phase:

  P1  register_ai_system, get_ai_system, list_ai_systems,
      assess_risk, submit_assessment, approve_assessment,
      get_system_risk_tier, record_trust_audit
  P3  check_release_gate
  P4  check_guardrails
  P5  record_change_event
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.trustplane.models.inventory import AISystem, RiskTier
    from app.trustplane.models.risk import RiskAssessment


async def register_ai_system(
    db: AsyncSession, org_id: str, user_id: str, **data
) -> AISystem:
    """Register a new AI system in the inventory (P1)."""
    from app.trustplane.services.inventory import create_system as _impl

    return await _impl(db, org_id, user_id, **data)


async def get_ai_system(
    db: AsyncSession, system_id: str, org_id: str
) -> AISystem:
    """Retrieve an AI system by ID and org (P1)."""
    from app.trustplane.services.inventory import get_system as _impl

    return await _impl(db, system_id, org_id)


async def list_ai_systems(
    db: AsyncSession, org_id: str, **filters
) -> tuple[list[AISystem], int]:
    """List AI systems for an org with optional filters (P1)."""
    from app.trustplane.services.inventory import list_systems as _impl

    return await _impl(db, org_id, **filters)


async def assess_risk(
    db: AsyncSession, system_id: str, org_id: str, user_id: str, **data
) -> RiskAssessment:
    """Create a new risk assessment for a system (P1)."""
    from app.trustplane.services.risk import create_assessment as _impl

    return await _impl(db, system_id, org_id, user_id, **data)


async def submit_assessment(
    db: AsyncSession, assessment_id: str, org_id: str, user_id: str
) -> RiskAssessment:
    """Submit a draft assessment for review (P1)."""
    from app.trustplane.services.risk import submit_assessment as _impl

    return await _impl(db, assessment_id, org_id, user_id)


async def approve_assessment(
    db: AsyncSession, assessment_id: str, org_id: str, reviewer_id: str
) -> RiskAssessment:
    """Approve a submitted assessment (P1)."""
    from app.trustplane.services.risk import approve_assessment as _impl

    return await _impl(db, assessment_id, org_id, reviewer_id)


async def get_system_risk_tier(
    db: AsyncSession, system_id: str, org_id: str
) -> RiskTier | None:
    """Return the current risk tier for a system, or None (P1)."""
    from app.trustplane.services.inventory import get_system as _impl

    system = await _impl(db, system_id, org_id)
    return system.risk_tier


async def record_trust_audit(db: AsyncSession, **kwargs) -> None:
    """Append an immutable trust audit event (P1)."""
    from app.trustplane.services.audit import record_trust_audit as _impl

    await _impl(db, **kwargs)


# ── Phase 3: Release Gates ───────────────────────────────────────────


async def check_release_gate(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    trigger: str,
    target_type: str,
    target_id: str,
    target_version: str | None = None,
) -> dict | None:
    """Check if a release gate blocks the given action (P3).

    Returns None if no active profile exists for this trigger (no gate).
    Returns {"outcome": "passed"|"failed", "profile_id": str, "result_id": str,
    "failed_checks": [...]} when a profile applies.

    Product code calls this before publishing a pack, approving an app,
    installing into a tenant, enabling a provider, or promoting an experiment.
    """
    from sqlalchemy import select

    from app.trustplane.models.gates import AssuranceProfile, ProfileStatus

    # Find active profile for this trigger in the org (or platform default)
    result = await db.execute(
        select(AssuranceProfile).where(
            AssuranceProfile.trigger == trigger,
            AssuranceProfile.status == ProfileStatus.ACTIVE,
            (AssuranceProfile.org_id == org_id) | (AssuranceProfile.org_id.is_(None)),
        )
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return None  # no gate configured

    from app.trustplane.services.gates import list_checks

    checks = await list_checks(db, profile.id, org_id)
    if not checks:
        return None  # profile has no checks

    # All checks start as "pending" — the caller must supply results
    # For now, return the gate metadata so the caller knows a gate applies
    return {
        "gate_required": True,
        "profile_id": profile.id,
        "profile_name": profile.name,
        "trigger": trigger,
        "checks": [
            {
                "check_id": c.id,
                "name": c.name,
                "check_type": c.check_type.value,
                "is_blocking": c.is_blocking,
            }
            for c in checks
        ],
    }


# ── Phase 4: Runtime Guardrails ──────────────────────────────────────


async def check_guardrails(
    db: AsyncSession,
    org_id: str,
    *,
    system_id: str | None = None,
    action_context: dict | None = None,
) -> list[dict]:
    """Evaluate active guardrails for a system/org before execution (P4).

    Returns a list of guardrail evaluations. Each is:
    {"policy_id": str, "name": str, "guardrail_type": str,
     "is_blocking": bool, "verdict": "allowed"|"blocked"|"escalated"}

    An empty list means no active guardrails apply. Product code (e.g.
    the workflow executor) calls this before making a provider call.
    """
    from sqlalchemy import select

    from app.trustplane.models.guardrails import GuardrailPolicy, GuardrailStatus

    base = select(GuardrailPolicy).where(
        GuardrailPolicy.org_id == org_id,
        GuardrailPolicy.status == GuardrailStatus.ACTIVE,
    )
    if system_id:
        # Match system-specific OR org-wide policies
        base = base.where(
            (GuardrailPolicy.system_id == system_id) | (GuardrailPolicy.system_id.is_(None))
        )
    else:
        base = base.where(GuardrailPolicy.system_id.is_(None))

    result = await db.execute(base.order_by(GuardrailPolicy.priority))
    policies = list(result.scalars().all())

    evaluations = []
    for policy in policies:
        evaluations.append(
            {
                "policy_id": policy.id,
                "name": policy.name,
                "guardrail_type": policy.guardrail_type.value,
                "is_blocking": policy.is_blocking,
                "verdict": "allowed",  # default; real enforcement in Phase 4+
                "config": policy.config,
            }
        )
    return evaluations


# ── Phase 5: Change Management ───────────────────────────────────────


async def record_change_event(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    *,
    system_id: str,
    change_type: str,
    title: str,
    before_value: dict | None = None,
    after_value: dict | None = None,
    impact: str = "low",
    detected_by: str = "system",
) -> str:
    """Record an assurance-changing event and return its ID (P5).

    Product code calls this when a model version changes, a provider
    is updated, a prompt template is modified, permissions change, etc.
    If impact is 'requires_revalidation', the affected system's evidence
    and assessments are flagged for revalidation.
    """
    from app.trustplane.services.changes import create_change_event as _impl

    event = await _impl(
        db,
        org_id,
        user_id,
        system_id=system_id,
        change_type=change_type,
        title=title,
        before_value=before_value,
        after_value=after_value,
        impact=impact,
        detected_by=detected_by,
    )
    return event.id
