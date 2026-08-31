"""Entitlement engine (ADR-014 §2) — full engine lands in P2.

P1 ships the registry defaults + a working check path (defaults only, no
plan/override resolution yet) so enforcement wiring is real from day one.
"""

from dataclasses import dataclass
from decimal import Decimal

import structlog

from app.exceptions import AppError

log = structlog.get_logger()

CACHE_KEY = "cp:ent:{tenant_id}"
CACHE_TTL_SECONDS = 60


@dataclass(frozen=True)
class EntitlementDef:
    key: str
    type: str  # "bool" | "int" | "decimal"
    default: object  # None on numeric = unlimited
    soft_capable: bool = False


ENTITLEMENT_DEFS: dict[str, EntitlementDef] = {
    d.key: d
    for d in [
        EntitlementDef("max_organizations", "int", 1),
        EntitlementDef("max_active_learners", "int", 25, soft_capable=True),
        EntitlementDef("max_instructors", "int", 3, soft_capable=True),
        EntitlementDef("max_storage_gb", "decimal", Decimal(5), soft_capable=True),
        EntitlementDef("max_ai_budget_usd_month", "decimal", None, soft_capable=True),
        EntitlementDef("max_workflow_runs_month", "int", 100),
        EntitlementDef("max_api_requests_day", "int", 10_000, soft_capable=True),
        EntitlementDef("custom_domain", "bool", False),
        EntitlementDef("white_label", "bool", False),
        EntitlementDef("client_portal", "bool", False),
        EntitlementDef("private_registry", "bool", True),
        EntitlementDef("paid_marketplace", "bool", False),
        EntitlementDef("advanced_analytics", "bool", False),
        EntitlementDef("webhooks", "bool", True),
        EntitlementDef("api_access", "bool", True),
    ]
}


@dataclass
class QuotaDecision:
    allowed: bool
    soft_warning: bool
    key: str
    limit: object
    current: object


async def get_effective(db, tenant) -> dict:
    """P1 interim: registry defaults only. P2 layers plan version + overrides
    + suspension mask + Redis caching on top of this shape."""
    return {k: d.default for k, d in ENTITLEMENT_DEFS.items()}


async def check_quota(db, tenant, key: str, *, current, requested=1) -> QuotaDecision:
    d = ENTITLEMENT_DEFS.get(key)
    if d is None:
        raise AppError("UNKNOWN_ENTITLEMENT", f"Unknown entitlement '{key}'", 422)
    effective = await get_effective(db, tenant)
    limit = effective.get(key)
    if limit is None:
        return QuotaDecision(True, False, key, None, current)
    if (Decimal(str(current)) + Decimal(str(requested))) <= Decimal(str(limit)):
        return QuotaDecision(True, False, key, limit, current)
    raise AppError(
        "QUOTA_EXCEEDED",
        f"Quota '{key}' exceeded (limit {limit}, current {current})",
        403,
    )


async def require_feature(db, tenant, key: str) -> None:
    d = ENTITLEMENT_DEFS.get(key)
    if d is None or d.type != "bool":
        raise AppError("UNKNOWN_ENTITLEMENT", f"Unknown feature '{key}'", 422)
    effective = await get_effective(db, tenant)
    if not effective.get(key):
        raise AppError(
            "FEATURE_NOT_AVAILABLE",
            f"Feature '{key}' is not available on your plan",
            403,
        )


async def invalidate_cache(tenant_id: str) -> None:
    """Drop the cached effective entitlements for a tenant (safe no-op on
    Redis failure — cache is TTL-bounded anyway)."""
    try:
        from app.core.redis import redis_pool

        r = redis_pool()
        await r.delete(CACHE_KEY.format(tenant_id=tenant_id))
    except Exception:  # noqa: BLE001 — cache invalidation must never break the write path
        log.debug("cp_ent_cache_invalidate_skipped", tenant_id=tenant_id)
