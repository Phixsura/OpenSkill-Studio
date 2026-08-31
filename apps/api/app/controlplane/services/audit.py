"""Commercial audit recording (ADR-014 §1.4).

record_audit() runs in the caller's transaction so the audit row commits
atomically with the business write it describes. Actions are validated
against the registry to prevent spelling drift.
"""

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.audit import CommercialAuditEvent

# Dotted action registry — covers every sensitive control-plane mutation
# listed in issue #27 §38. Additions require updating this set (tests assert
# every record_audit call site uses a registered action).
AUDIT_ACTIONS = frozenset(
    {
        # tenants
        "tenant.created",
        "tenant.suspended",
        "tenant.reactivated",
        "tenant.status_changed",
        "tenant.provisioned",
        "tenant.export_created",
        "tenant.currency_changed",
        "tenant.attribution_set",
        "tenant.attribution_cleared",
        # platform roles
        "platform_role.granted",
        "platform_role.revoked",
        # plans / entitlements
        "plan.version_activated",
        "subscription.plan_changed",
        "entitlement.override_set",
        "entitlement.override_removed",
        # pricing
        "pricing.policy_created",
        "pricing.policy_deactivated",
        "pricing.cost_rate_created",
        "pricing.cost_rate_superseded",
        "fx.rate_created",
        # usage
        "usage.adjusted",
        "rated_usage.voided",
        # credits
        "credit.topped_up",
        "credit.promotional_granted",
        "credit.adjusted",
        "credit.refunded",
        # invoices
        "invoice.finalized",
        "invoice.payment_recorded",
        "invoice.voided",
        "invoice.credit_note_issued",
        # revenue share / settlements
        "revshare.rule_activated",
        "revshare.rule_retired",
        "revshare.entry_adjusted",
        "settlement.finalized",
        "settlement.approved",
        "settlement.marked_paid",
        "settlement.adjusted",
        # domains / branding
        "domain.created",
        "domain.verified",
        "domain.activated",
        "domain.disabled",
        "branding.updated",
        # impersonation
        "impersonation.grant_created",
        "impersonation.token_minted",
        "impersonation.grant_revoked",
        # client portal
        "client_link.created",
        "client_link.revoked",
        # marketplace
        "license.granted_manually",
        "license.revoked",
        "purchase.refunded",
        "listing.commission_changed",
    }
)


@dataclass(frozen=True)
class Actor:
    """Who performed the action, resolved by the endpoint layer."""

    user_id: str | None
    type: str  # platform | tenant | partner | system | impersonated
    request_id: str | None = None


SYSTEM_ACTOR = Actor(user_id=None, type="system")


async def record_audit(
    db: AsyncSession,
    *,
    actor: Actor,
    action: str,
    target_type: str,
    target_id: str,
    tenant_id: str | None = None,
    partner_id: str | None = None,
    before: dict | None = None,
    after: dict | None = None,
    reason: str | None = None,
) -> CommercialAuditEvent:
    if action not in AUDIT_ACTIONS:
        raise ValueError(f"Unregistered audit action: {action}")
    event = CommercialAuditEvent(
        actor_user_id=actor.user_id,
        actor_type=actor.type,
        action=action,
        target_type=target_type,
        target_id=target_id,
        tenant_id=tenant_id,
        partner_id=partner_id,
        before=before,
        after=after,
        reason=reason,
        request_id=actor.request_id,
    )
    db.add(event)
    return event


# Actions a tenant may see about itself. Platform-internal actions (cost
# rates, fx, settlements of other beneficiaries, impersonation of other
# tenants' users) are filtered out of the tenant-scoped audit endpoint.
TENANT_VISIBLE_ACTIONS = frozenset(
    {
        "tenant.created",
        "tenant.suspended",
        "tenant.reactivated",
        "tenant.status_changed",
        "tenant.currency_changed",
        "subscription.plan_changed",
        "entitlement.override_set",
        "entitlement.override_removed",
        "credit.topped_up",
        "credit.promotional_granted",
        "credit.adjusted",
        "credit.refunded",
        "invoice.finalized",
        "invoice.payment_recorded",
        "invoice.voided",
        "invoice.credit_note_issued",
        "domain.created",
        "domain.verified",
        "domain.activated",
        "domain.disabled",
        "branding.updated",
        "client_link.created",
        "client_link.revoked",
        "license.granted_manually",
        "license.revoked",
        "purchase.refunded",
    }
)
