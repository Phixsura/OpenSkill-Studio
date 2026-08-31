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


async def check_install_license(db: AsyncSession, product_type: str, product_id: str, org) -> None:
    """Marketplace license gate for pack/path installation (P8)."""
    from app.controlplane.services.marketplace import check_install_license as _impl

    await _impl(db, product_type, product_id, org)
