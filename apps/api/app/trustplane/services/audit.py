"""Trust audit recording (ADR-017 §P).

record_trust_audit() runs in the caller's transaction so the audit row
commits atomically with the business write it describes. Actions are
validated against the frozen registry to prevent spelling drift.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.trustplane.models.audit import TrustAuditEvent

# Dotted action registry — covers every trust-plane mutation.
# Additions require updating this set (tests assert every
# record_trust_audit call site uses a registered action).
TRUST_AUDIT_ACTIONS = frozenset(
    {
        # AI systems
        "system.created",
        "system.updated",
        "system.lifecycle_changed",
        "system.owner_changed",
        "system.linked",
        # use cases
        "use_case.created",
        "use_case.updated",
        "use_case.deleted",
        # risk assessments
        "assessment.created",
        "assessment.submitted",
        "assessment.approved",
        "assessment.rejected",
        "assessment.superseded",
        "assessment.tier_overridden",
        # scoring policies
        "policy.created",
        "policy.updated",
        "policy.activated",
        "policy.deactivated",
        # assurance cases (Phase 2)
        "case.created",
        "case.updated",
        "case.status_changed",
        # evidence items (Phase 2)
        "evidence.created",
        "evidence.updated",
        "evidence.status_changed",
        "evidence.linked",
        "evidence.unlinked",
        # reviews (Phase 2)
        "review.created",
        "review.assigned",
        "review.decided",
        "review.cancelled",
        "review.expired",
        # assurance profiles & gates (Phase 3)
        "profile.created",
        "profile.activated",
        "gate.evaluated",
        "gate.overridden",
        # guardrails & boundaries (Phase 4)
        "guardrail.created",
        "guardrail.activated",
        "guardrail.disabled",
        "boundary.created",
        # monitoring & incidents (Phase 5)
        "monitor.created",
        "incident.created",
        "incident.status_changed",
        "incident.action_added",
    }
)


async def record_trust_audit(
    db: AsyncSession,
    *,
    org_id: str,
    actor_user_id: str | None,
    actor_type: str,
    action: str,
    target_type: str,
    target_id: str,
    before: dict | None = None,
    after: dict | None = None,
    reason: str | None = None,
    request_id: str | None = None,
) -> TrustAuditEvent:
    if action not in TRUST_AUDIT_ACTIONS:
        raise ValueError(f"Unregistered trust audit action: {action}")
    event = TrustAuditEvent(
        org_id=org_id,
        actor_user_id=actor_user_id,
        actor_type=actor_type,
        action=action,
        target_type=target_type,
        target_id=target_id,
        before=before,
        after=after,
        reason=reason,
        request_id=request_id,
    )
    db.add(event)
    return event
