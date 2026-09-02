"""Plan and plan-version lifecycle (ADR-014 §2)."""

from datetime import UTC, datetime

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.plan import (
    PlanPrice,
    PlanVersion,
    ProductPlan,
    TenantEntitlementOverride,
)
from app.controlplane.services.audit import Actor, record_audit
from app.controlplane.services.entitlements import (
    invalidate_cache,
    invalidate_cache_for_plan,
    validate_entitlement_value,
)
from app.exceptions import AppError

log = structlog.get_logger()


async def create_plan(
    db: AsyncSession, *, key: str, name: str, description: str | None, actor: Actor
) -> ProductPlan:
    exists = await db.execute(select(ProductPlan.id).where(ProductPlan.key == key).limit(1))
    if exists.scalar_one_or_none() is not None:
        raise AppError("PLAN_EXISTS", f"Plan '{key}' already exists", 409)
    plan = ProductPlan(key=key, name=name, description=description)
    db.add(plan)
    await db.flush()
    return plan


async def create_draft_version(
    db: AsyncSession, plan: ProductPlan, *, created_by: str | None
) -> PlanVersion:
    """New draft cloning the current active version's entitlements + prices."""
    latest = (
        await db.execute(
            select(func.max(PlanVersion.version)).where(PlanVersion.plan_id == plan.id)
        )
    ).scalar_one()
    active = (
        await db.execute(
            select(PlanVersion).where(
                PlanVersion.plan_id == plan.id, PlanVersion.status == "active"
            )
        )
    ).scalar_one_or_none()
    draft = PlanVersion(
        plan_id=plan.id,
        version=(latest or 0) + 1,
        status="draft",
        entitlements=dict(active.entitlements) if active else {},
        created_by=created_by,
    )
    db.add(draft)
    await db.flush()
    if active:
        prices = (
            (await db.execute(select(PlanPrice).where(PlanPrice.plan_version_id == active.id)))
            .scalars()
            .all()
        )
        for p in prices:
            db.add(
                PlanPrice(
                    plan_version_id=draft.id,
                    currency=p.currency,
                    interval=p.interval,
                    amount_minor=p.amount_minor,
                    included_seats=p.included_seats,
                    overage_seat_amount_minor=p.overage_seat_amount_minor,
                    # external_price_ref NOT cloned — a new version needs a new
                    # Stripe price object
                )
            )
        await db.flush()
    return draft


def _require_draft(version: PlanVersion) -> None:
    if version.status != "draft":
        raise AppError(
            "PLAN_VERSION_IMMUTABLE",
            "Only draft plan versions can be modified",
            409,
        )


async def update_draft(
    db: AsyncSession,
    version: PlanVersion,
    *,
    entitlements: dict | None = None,
    prices: list[dict] | None = None,
) -> PlanVersion:
    _require_draft(version)
    if entitlements is not None:
        validated = {k: validate_entitlement_value(k, v) for k, v in entitlements.items()}
        version.entitlements = validated
    if prices is not None:
        # Replace-all semantics for draft prices (simplest correct editor model)
        existing = (
            (await db.execute(select(PlanPrice).where(PlanPrice.plan_version_id == version.id)))
            .scalars()
            .all()
        )
        for p in existing:
            await db.delete(p)
        # R62[1]: flush the DELETEs BEFORE adding replacements. SQLAlchemy
        # orders INSERTs before DELETEs within one flush, so re-adding the
        # same (currency, interval) — the normal "edit the amount" PATCH —
        # hit uq_cp_plan_price as an unhandled IntegrityError 500.
        await db.flush()
        for p in prices:
            db.add(
                PlanPrice(
                    plan_version_id=version.id,
                    currency=p["currency"],
                    interval=p["interval"],
                    amount_minor=p["amount_minor"],
                    included_seats=p.get("included_seats", 0),
                    overage_seat_amount_minor=p.get("overage_seat_amount_minor"),
                )
            )
    await db.flush()
    return version


async def activate_version(db: AsyncSession, version: PlanVersion, *, actor: Actor) -> PlanVersion:
    """draft → active; retires the previous active version in the same tx.

    Guarded transitions + the uq_cp_plan_active partial index make the race
    a deterministic 409 instead of two active versions.
    """
    _require_draft(version)
    # R62[3]: serialize concurrent activations of DIFFERENT drafts on the
    # PLAN row. Under READ COMMITTED, B's retire-UPDATE scan does not pick up
    # A's newly-activated row, so B's insert of a second 'active' hit
    # uq_cp_plan_active as an unhandled IntegrityError 500 instead of the
    # documented 409. With the plan lock, B re-reads AFTER A commits, retires
    # A's version cleanly, and the last activation deterministically wins.
    await db.execute(
        select(ProductPlan.id).where(ProductPlan.id == version.plan_id).with_for_update()
    )
    # Retire current active (guarded — 0 rows is fine, plan may have none)
    await db.execute(
        update(PlanVersion)
        .where(
            PlanVersion.plan_id == version.plan_id,
            PlanVersion.status == "active",
        )
        .values(status="retired")
    )
    result = await db.execute(
        update(PlanVersion)
        .where(PlanVersion.id == version.id, PlanVersion.status == "draft")
        .values(status="active", activated_at=datetime.now(UTC))
    )
    if not result.rowcount:
        raise AppError("PLAN_VERSION_CONFLICT", "Version activated concurrently", 409)
    await record_audit(
        db,
        actor=actor,
        action="plan.version_activated",
        target_type="plan_version",
        target_id=version.id,
        after={"plan_id": version.plan_id, "version": version.version},
    )
    await invalidate_cache_for_plan(db, version.plan_id)
    await db.refresh(version)
    return version


# ── Overrides ────────────────────────────────────────────────


async def set_override(
    db: AsyncSession,
    tenant_id: str,
    key: str,
    *,
    value: object,
    enforcement: str,
    expires_at: datetime | None,
    reason: str,
    actor: Actor,
) -> TenantEntitlementOverride:
    normalized = validate_entitlement_value(key, value)
    if enforcement not in ("hard", "soft"):
        raise AppError("VALIDATION_ERROR", "enforcement must be hard|soft", 422)
    existing = (
        await db.execute(
            select(TenantEntitlementOverride).where(
                TenantEntitlementOverride.tenant_id == tenant_id,
                TenantEntitlementOverride.key == key,
            )
        )
    ).scalar_one_or_none()
    before = None
    if existing is not None:
        before = {"value": existing.value.get("v"), "enforcement": existing.enforcement}
        existing.value = {"v": normalized}
        existing.enforcement = enforcement
        existing.expires_at = expires_at
        existing.reason = reason
        override = existing
    else:
        override = TenantEntitlementOverride(
            tenant_id=tenant_id,
            key=key,
            value={"v": normalized},
            enforcement=enforcement,
            expires_at=expires_at,
            reason=reason,
            created_by=actor.user_id,
        )
        db.add(override)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="entitlement.override_set",
        target_type="tenant",
        target_id=tenant_id,
        tenant_id=tenant_id,
        before=before,
        after={"key": key, "value": normalized, "enforcement": enforcement},
        reason=reason,
    )
    await invalidate_cache(tenant_id)
    return override


async def remove_override(db: AsyncSession, tenant_id: str, key: str, *, actor: Actor) -> None:
    existing = (
        await db.execute(
            select(TenantEntitlementOverride).where(
                TenantEntitlementOverride.tenant_id == tenant_id,
                TenantEntitlementOverride.key == key,
            )
        )
    ).scalar_one_or_none()
    if existing is None:
        raise AppError("OVERRIDE_NOT_FOUND", "Override not found", 404)
    await record_audit(
        db,
        actor=actor,
        action="entitlement.override_removed",
        target_type="tenant",
        target_id=tenant_id,
        tenant_id=tenant_id,
        before={"key": key, "value": existing.value.get("v")},
    )
    await db.delete(existing)
    await db.flush()
    await invalidate_cache(tenant_id)
