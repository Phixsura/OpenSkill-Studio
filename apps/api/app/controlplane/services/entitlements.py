"""Entitlement engine (ADR-014 §2).

Effective entitlements = plan defaults (from the tenant's live subscription's
plan version; TRIAL tenants get the school plan; otherwise community/registry
defaults) + non-expired overrides − suspension mask. Cached in Redis (60s TTL,
explicit invalidation); Redis failure falls back to the DB — never fail-open.

Override rows store values wrapped as {"v": <value>} so scalar JSON types
survive the JSONB column with typed validation on the way in/out.
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.tenant import (
    TENANT_BLOCKED_STATUSES,
    TenantAccount,
    TenantStatus,
)
from app.exceptions import AppError

log = structlog.get_logger()

CACHE_KEY = "cp:ent:{tenant_id}"
# R55[1]: invalidation tombstone — while present, get_effective computes from
# DB but does NOT re-cache (a reader racing an uncommitted mutation would
# otherwise re-populate the stale value for the full TTL). The TTL only needs
# to outlive the mutation's commit window.
DIRTY_KEY = "cp:entdirty:{tenant_id}"
# R97[m14]: 5s assumed request-scale commits; outbox handlers can run tens of
# seconds between invalidate and their per-message commit (rating batches,
# provider calls). 30s covers the per-message commit window (R89[12]) with
# margin while keeping the no-cache penalty short.
DIRTY_TTL_SECONDS = 30
CACHE_TTL_SECONDS = 60

# The plan trials run on (ADR-014 §1.3) and the no-subscription fallback.
TRIAL_PLAN_KEY = "school"
DEFAULT_PLAN_KEY = "community"

# Boolean entitlements that represent CONSUMPTION and are masked off while a
# tenant is suspended. Display/white-label entitlements stay on (an active
# custom domain doesn't go dark just because consumption is paused).
SUSPENSION_MASKED_KEYS = frozenset({"client_portal", "paid_marketplace", "webhooks", "api_access"})


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


def validate_entitlement_value(key: str, value: object) -> object:
    """Typed validation for plan-version / override writes. Returns the
    normalized value or raises UNKNOWN_ENTITLEMENT."""
    d = ENTITLEMENT_DEFS.get(key)
    if d is None:
        raise AppError("UNKNOWN_ENTITLEMENT", f"Unknown entitlement '{key}'", 422)
    if value is None:
        if d.type == "bool":
            raise AppError("UNKNOWN_ENTITLEMENT", f"'{key}' cannot be null", 422)
        return None  # numeric None = unlimited
    if d.type == "bool":
        if not isinstance(value, bool):
            raise AppError("UNKNOWN_ENTITLEMENT", f"'{key}' expects a boolean", 422)
        return value
    if d.type == "int":
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise AppError("UNKNOWN_ENTITLEMENT", f"'{key}' expects a non-negative integer", 422)
        return value
    # decimal — accept int/str, reject float noise. Order matters: NaN
    # compares by RAISING InvalidOperation, so is_finite() must come first.
    try:
        dec = Decimal(str(value)) if not isinstance(value, bool) else None
    except InvalidOperation:
        dec = None
    if dec is None or not dec.is_finite() or dec < 0:
        raise AppError("UNKNOWN_ENTITLEMENT", f"'{key}' expects a non-negative decimal", 422)
    return str(dec)  # stored as string in JSONB for precision


@dataclass
class EffectiveEntitlements:
    values: dict[str, object]
    sources: dict[str, str]  # key -> default|plan|override|suspension
    enforcement: dict[str, str] = field(default_factory=dict)  # key -> hard|soft (overrides only)
    plan_key: str | None = None
    plan_version: int | None = None
    trial: bool = False

    def get(self, key: str):
        v = self.values.get(key)
        d = ENTITLEMENT_DEFS[key]
        if d.type == "decimal" and isinstance(v, str):
            return Decimal(v)
        return v


@dataclass
class QuotaDecision:
    allowed: bool
    soft_warning: bool
    key: str
    limit: object
    current: object


async def _resolve_plan_version(db: AsyncSession, tenant: TenantAccount):
    """Return (PlanVersion|None, plan_key, trial_flag) for the tenant."""
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    # Live subscription wins (statuses that keep plan entitlements).
    try:
        from app.controlplane.models.billing import Subscription  # P6

        sub = (
            await db.execute(
                select(Subscription)
                .where(
                    Subscription.tenant_id == tenant.id,
                    Subscription.status.in_(
                        ["trial", "active", "past_due", "cancel_at_period_end"]
                    ),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
    except ImportError:  # billing lands in P6
        sub = None
    if sub is not None:
        pv = await db.get(PlanVersion, sub.plan_version_id)
        if pv is not None:
            plan = await db.get(ProductPlan, pv.plan_id)
            return pv, (plan.key if plan else None), False

    # Unexpired trial → school plan defaults.
    if (
        tenant.status == TenantStatus.TRIAL
        and tenant.trial_ends_at is not None
        and tenant.trial_ends_at > datetime.now(UTC)
    ):
        row = (
            await db.execute(
                select(PlanVersion)
                .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
                .where(ProductPlan.key == TRIAL_PLAN_KEY, PlanVersion.status == "active")
                .limit(1)
            )
        ).scalar_one_or_none()
        if row is not None:
            return row, TRIAL_PLAN_KEY, True
    return None, DEFAULT_PLAN_KEY, False


async def _compute_effective(db: AsyncSession, tenant: TenantAccount) -> EffectiveEntitlements:
    from app.controlplane.models.plan import TenantEntitlementOverride

    values: dict[str, object] = {k: d.default for k, d in ENTITLEMENT_DEFS.items()}
    # normalize decimals to str for cache-serializability
    for k, d in ENTITLEMENT_DEFS.items():
        if d.type == "decimal" and isinstance(values[k], Decimal):
            values[k] = str(values[k])
    sources = {k: "default" for k in ENTITLEMENT_DEFS}
    enforcement: dict[str, str] = {}

    pv, plan_key, trial = await _resolve_plan_version(db, tenant)
    if pv is not None:
        for k, v in pv.entitlements.items():
            if k in ENTITLEMENT_DEFS:
                values[k] = v
                sources[k] = "plan"

    now = datetime.now(UTC)
    overrides = (
        (
            await db.execute(
                select(TenantEntitlementOverride).where(
                    TenantEntitlementOverride.tenant_id == tenant.id
                )
            )
        )
        .scalars()
        .all()
    )
    for o in overrides:
        if o.key not in ENTITLEMENT_DEFS:
            continue
        if o.expires_at is not None and o.expires_at <= now:
            continue  # expired grants filter live — no cron needed
        values[o.key] = o.value.get("v")
        sources[o.key] = "override"
        enforcement[o.key] = o.enforcement

    # R49[35]: the mask must cover every blocked status. TENANT_BLOCKED_STATUSES
    # is {SUSPENDED, CANCELLED, ARCHIVED} — a cancelled/archived tenant kept
    # webhooks/api_access/client_portal/paid_marketplace open because only
    # SUSPENDED was checked here, so endpoints gated purely by entitlements
    # (not require_tenant_active) stayed live after cancellation.
    if tenant.status in TENANT_BLOCKED_STATUSES:
        for k in SUSPENSION_MASKED_KEYS:
            values[k] = False
            sources[k] = "suspension"

    return EffectiveEntitlements(
        values=values,
        sources=sources,
        enforcement=enforcement,
        plan_key=plan_key,
        plan_version=pv.version if pv else None,
        trial=trial,
    )


async def get_effective(db: AsyncSession, tenant: TenantAccount) -> EffectiveEntitlements:
    """Cached effective entitlements. Redis miss/error → compute from DB."""
    key = CACHE_KEY.format(tenant_id=tenant.id)
    try:
        from app.core.redis import redis_pool

        r = redis_pool()
        cached = await r.get(key)
        if cached:
            data = json.loads(cached)
            return EffectiveEntitlements(**data)
    except Exception:  # noqa: BLE001 — cache is an optimization, never a gate
        pass
    eff = await _compute_effective(db, tenant)
    try:
        from app.core.redis import redis_pool

        r = redis_pool()
        # R55[1]: services invalidate BEFORE the router commits — a concurrent
        # reader could recompute from the pre-write DB snapshot and re-cache
        # the STALE value for the full TTL. invalidate_cache leaves a short
        # dirty tombstone; while it lives, readers compute from DB but never
        # write the cache, so nothing stale outlives the mutation's commit.
        if await r.get(DIRTY_KEY.format(tenant_id=tenant.id)):
            return eff
        await r.set(
            key,
            json.dumps(
                {
                    "values": eff.values,
                    "sources": eff.sources,
                    "enforcement": eff.enforcement,
                    "plan_key": eff.plan_key,
                    "plan_version": eff.plan_version,
                    "trial": eff.trial,
                }
            ),
            ex=CACHE_TTL_SECONDS,
        )
    except Exception:  # noqa: BLE001
        pass
    return eff


async def invalidate_cache(tenant_id: str) -> None:
    """Drop cached entitlements (safe no-op on Redis failure — TTL bounds
    staleness anyway)."""
    try:
        from app.core.redis import redis_pool

        r = redis_pool()
        # R55[1]: tombstone first (see get_effective) so a reader racing the
        # not-yet-committed mutation can't re-populate the stale value.
        await r.set(DIRTY_KEY.format(tenant_id=tenant_id), "1", ex=DIRTY_TTL_SECONDS)
        await r.delete(CACHE_KEY.format(tenant_id=tenant_id))
        # R55[2]: the API-metering middleware keeps a SECOND cache of the
        # resolved max_api_requests_day (cp:apiquota:*, 300s) that nothing
        # ever invalidated — plan upgrades kept 429ing at the old limit for
        # up to 5 minutes. Every entitlement-cache invalidation drops it too.
        await r.delete(f"cp:apiquota:{tenant_id}")
    except Exception:  # noqa: BLE001
        log.debug("cp_ent_cache_invalidate_skipped", tenant_id=tenant_id)


async def invalidate_cache_for_plan(db: AsyncSession, plan_id: str) -> None:
    """On version activation: drop cache for every tenant subscribed to the plan."""
    try:
        from app.controlplane.models.billing import Subscription
        from app.controlplane.models.plan import PlanVersion

        tenant_ids = (
            (
                await db.execute(
                    select(Subscription.tenant_id)
                    .join(PlanVersion, PlanVersion.id == Subscription.plan_version_id)
                    .where(PlanVersion.plan_id == plan_id)
                    .distinct()
                )
            )
            .scalars()
            .all()
        )
    except ImportError:
        tenant_ids = []
    for tid in tenant_ids:
        await invalidate_cache(tid)


# ── Enforcement API (facade-exposed) ─────────────────────────


async def check_quota(
    db: AsyncSession, tenant: TenantAccount, key: str, *, current, requested=1
) -> QuotaDecision:
    d = ENTITLEMENT_DEFS.get(key)
    if d is None or d.type == "bool":
        raise AppError("UNKNOWN_ENTITLEMENT", f"Unknown numeric entitlement '{key}'", 422)
    eff = await get_effective(db, tenant)
    limit = eff.get(key)
    if limit is None:
        return QuotaDecision(True, False, key, None, current)
    if (Decimal(str(current)) + Decimal(str(requested))) <= Decimal(str(limit)):
        return QuotaDecision(True, False, key, limit, current)
    # Over the limit: soft when the override says so, or (no override) the
    # plan default policy — v1: storage is soft by default, others hard.
    soft = eff.enforcement.get(key) == "soft" or (
        key not in eff.enforcement and key == "max_storage_gb"
    )
    if soft and d.soft_capable:
        log.warning("cp_quota_soft_exceeded", key=key, tenant_id=tenant.id, limit=str(limit))
        return QuotaDecision(True, True, key, limit, current)
    raise AppError(
        "QUOTA_EXCEEDED",
        f"Quota '{key}' exceeded (limit {limit}, current {current})",
        403,
    )


async def require_feature(db: AsyncSession, tenant: TenantAccount, key: str) -> None:
    d = ENTITLEMENT_DEFS.get(key)
    if d is None or d.type != "bool":
        raise AppError("UNKNOWN_ENTITLEMENT", f"Unknown feature '{key}'", 422)
    eff = await get_effective(db, tenant)
    if not eff.values.get(key):
        raise AppError(
            "FEATURE_NOT_AVAILABLE",
            f"Feature '{key}' is not available on your plan",
            403,
        )
