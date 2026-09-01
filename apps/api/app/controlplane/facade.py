"""The ONLY control-plane import surface for product code.

Product services/routers call these functions; they must never import
`app.controlplane.models` / `app.controlplane.services` directly, so the
commercial domain can evolve without rippling through the product layer.

Functions are thin delegations — the real logic lives in
app/controlplane/services/*. Each is filled in by its owning phase:

  P1  get_tenant_for_org, require_tenant_active, record_audit
  P2  check_quota, require_feature, get_effective_entitlements
  P3  emit_usage
  P8  check_install_license
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def get_tenant_for_org(db: AsyncSession, org_id: str):
    """Resolve the owning TenantAccount for an organization (P1)."""
    from app.controlplane.services.tenants import get_tenant_for_org as _impl

    return await _impl(db, org_id)


def require_tenant_active(tenant) -> None:
    """Raise TENANT_SUSPENDED (403) when the tenant may not consume (P1)."""
    from app.controlplane.services.tenants import require_tenant_active as _impl

    _impl(tenant)


async def record_audit(db: AsyncSession, **kwargs) -> None:
    """Append an immutable commercial audit event (P1)."""
    from app.controlplane.services.audit import record_audit as _impl

    await _impl(db, **kwargs)


async def get_effective_entitlements(db: AsyncSession, tenant):
    """Effective entitlements: plan defaults + overrides − suspension (P2)."""
    from app.controlplane.services.entitlements import get_effective as _impl

    return await _impl(db, tenant)


async def check_budget(
    db: AsyncSession,
    tenant,
    org_id: str | None,
    *,
    project_id: str | None = None,
    cohort_id: str | None = None,
    user_id: str | None = None,
    capability: str | None = None,
    usage_type: str | None = None,
    projected_minor: int = 0,
):
    """Enforce all matching budget policies + the tenant AI ceiling (P5).

    Hard-stop policies raise BUDGET_EXCEEDED (429); returns a BudgetDecision
    whose `warnings` carry soft/threshold signals. Every costed product path
    (workflow runs, evaluations) must call this — it was previously reachable
    only from the evaluation service, leaving workflow spend unbounded (R63).
    """
    from app.controlplane.services.budgets import check as _impl

    return await _impl(
        db,
        tenant,
        org_id,
        project_id=project_id,
        cohort_id=cohort_id,
        user_id=user_id,
        capability=capability,
        usage_type=usage_type,
        projected_minor=projected_minor,
    )


async def check_quota(db: AsyncSession, tenant, key: str, *, current, requested=1):
    """Enforce a numeric entitlement; hard limits raise QUOTA_EXCEEDED (P2)."""
    from app.controlplane.services.entitlements import check_quota as _impl

    return await _impl(db, tenant, key, current=current, requested=requested)


async def require_feature(db: AsyncSession, tenant, key: str) -> None:
    """Enforce a boolean entitlement; raises FEATURE_NOT_AVAILABLE (P2)."""
    from app.controlplane.services.entitlements import require_feature as _impl

    await _impl(db, tenant, key)


async def emit_usage(db: AsyncSession, **kwargs):
    """Append a UsageEvent + outbox message in the caller's transaction (P3).

    Idempotent on idempotency_key: returns None when a duplicate is ignored.
    Never commits — atomicity with the business write is the caller's.
    """
    from app.controlplane.services.metering import emit_usage as _impl

    return await _impl(db, **kwargs)


async def check_storage_quota(db: AsyncSession, org_id: str, incoming_bytes: int) -> None:
    """Enforce max_storage_gb for the org's tenant before accepting an upload.

    Live SUM at upload time (ADR-014 §2.5 decision) over submission_items +
    project_assets across the tenant's orgs. Storage is soft-by-default —
    check_quota resolves the soft path (warning, not rejection).
    """
    from decimal import Decimal

    from sqlalchemy import func, select

    from app.controlplane.services.entitlements import check_quota as _check
    from app.controlplane.services.tenants import get_tenant_for_org as _tenant
    from app.models.organization import Organization
    from app.models.project import ProjectAsset, Submission, SubmissionItem

    tenant = await _tenant(db, org_id)
    org_ids = select(Organization.id).where(Organization.tenant_id == tenant.id)
    item_bytes = (
        await db.execute(
            select(func.coalesce(func.sum(SubmissionItem.file_size), 0))
            .join(Submission, Submission.id == SubmissionItem.submission_id)
            .where(Submission.org_id.in_(org_ids))
        )
    ).scalar_one()
    asset_bytes = (
        await db.execute(
            select(func.coalesce(func.sum(ProjectAsset.file_size), 0)).where(
                ProjectAsset.org_id.in_(org_ids)
            )
        )
    ).scalar_one()
    current_gb = Decimal(item_bytes + asset_bytes) / Decimal(1073741824)
    incoming_gb = Decimal(incoming_bytes) / Decimal(1073741824)
    await _check(
        db,
        tenant,
        "max_storage_gb",
        current=current_gb.quantize(Decimal("0.000001")),
        requested=incoming_gb.quantize(Decimal("0.000001")),
    )


async def check_install_license(db: AsyncSession, product_type: str, product_id: str, org) -> None:
    """Marketplace license gate for pack/path installation (P8)."""
    from app.controlplane.services.marketplace import check_install_license as _impl

    await _impl(db, product_type, product_id, org)
