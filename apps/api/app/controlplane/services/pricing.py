"""Cost-rate / price-policy / FX-rate management (ADR-014 §4.6)."""

from datetime import datetime
from decimal import Decimal, InvalidOperation

import structlog
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.outbox import enqueue
from app.controlplane.models.pricing import (
    POLICY_TYPES,
    FxRate,
    PricePolicy,
    ProviderCostRate,
)
from app.controlplane.models.usage import USAGE_TYPES
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()


def validate_policy_params(policy_type: str, params: dict) -> dict:
    """Per-type discriminated schema (extra keys rejected)."""
    if policy_type not in POLICY_TYPES:
        raise AppError("INVALID_POLICY_PARAMS", f"Unknown policy type '{policy_type}'", 422)

    def dec(key: str, *, positive: bool = True, nonzero: bool = False) -> Decimal:
        try:
            v = Decimal(str(params[key]))
        except (KeyError, InvalidOperation) as exc:
            raise AppError(
                "INVALID_POLICY_PARAMS", f"params.{key} invalid or missing", 422
            ) from exc
        if not v.is_finite() or (positive and v < 0):
            raise AppError("INVALID_POLICY_PARAMS", f"params.{key} must be non-negative", 422)
        if nonzero and v == 0:
            # per_quantity is a divisor at rating time — 0 passed the old
            # non-negative check then raised DivisionByZero in rate_event,
            # dead-lettering the tenant's rating + run.terminal settlement
            # (R52[12]). Reject it at policy-create instead.
            raise AppError("INVALID_POLICY_PARAMS", f"params.{key} must be positive", 422)
        return v

    def intval(key: str) -> int:
        v = params.get(key)
        if isinstance(v, bool) or not isinstance(v, int) or v < 0:
            raise AppError("INVALID_POLICY_PARAMS", f"params.{key} must be a non-negative int", 422)
        # R99[m22]: no ceiling let 10^19 params store fine and overflow int8
        # at rating time (asyncpg DataError on every matching event forever).
        # Same money ceiling as the endpoint-level minor fields (R88).
        if v > 1_000_000_000_000_000:
            raise AppError(
                "INVALID_POLICY_PARAMS", f"params.{key} exceeds the maximum (10^15)", 422
            )
        return v

    allowed: set[str]
    if policy_type == "cost_plus_percentage":
        dec("percentage")
        allowed = {"percentage", "exclude_failed"}
    elif policy_type == "cost_plus_fixed":
        intval("fixed_markup_minor")
        if "per_quantity" in params:
            dec("per_quantity", nonzero=True)
        allowed = {"fixed_markup_minor", "per_quantity", "exclude_failed"}
    elif policy_type == "fixed_unit_price":
        intval("unit_price_minor")
        if "per_quantity" in params:
            dec("per_quantity", nonzero=True)
        allowed = {"unit_price_minor", "per_quantity", "exclude_failed"}
    else:  # included_quota_then_overage
        dec("included_quota")
        intval("overage_unit_price_minor")
        if "per_quantity" in params:
            dec("per_quantity", nonzero=True)
        allowed = {"included_quota", "overage_unit_price_minor", "per_quantity", "exclude_failed"}
    extra = set(params.keys()) - allowed
    if extra:
        raise AppError("INVALID_POLICY_PARAMS", f"Unknown params: {sorted(extra)}", 422)
    if "exclude_failed" in params and not isinstance(params["exclude_failed"], bool):
        raise AppError("INVALID_POLICY_PARAMS", "params.exclude_failed must be a boolean", 422)
    return params


async def _check_cost_rate_overlap(
    db: AsyncSession,
    *,
    provider: str,
    model_or_service: str | None,
    usage_type: str,
    capability_key: str | None,
    effective_from: datetime,
    effective_until: datetime | None,
) -> None:
    """No overlapping [from, until) windows for the same dimensions."""
    conds = [
        ProviderCostRate.provider == provider,
        ProviderCostRate.usage_type == usage_type,
        (
            ProviderCostRate.model_or_service == model_or_service
            if model_or_service is not None
            else ProviderCostRate.model_or_service.is_(None)
        ),
        (
            ProviderCostRate.capability_key == capability_key
            if capability_key is not None
            else ProviderCostRate.capability_key.is_(None)
        ),
        # window intersection: existing.from < new.until AND existing.until > new.from
        or_(
            ProviderCostRate.effective_until.is_(None),
            ProviderCostRate.effective_until > effective_from,
        ),
    ]
    if effective_until is not None:
        conds.append(ProviderCostRate.effective_from < effective_until)
    overlap = (
        await db.execute(select(ProviderCostRate.id).where(and_(*conds)).limit(1))
    ).scalar_one_or_none()
    if overlap is not None:
        raise AppError(
            "COST_RATE_OVERLAP", "Overlapping effective window for these dimensions", 409
        )


async def create_cost_rate(db: AsyncSession, *, actor: Actor, **fields) -> ProviderCostRate:
    usage_type = fields["usage_type"]
    unit = USAGE_TYPES.get(usage_type)
    if unit is None:
        raise AppError("UNKNOWN_USAGE_TYPE", f"Unknown usage type '{usage_type}'", 422)
    if fields.get("unit") not in (None, unit):
        raise AppError("VALIDATION_ERROR", f"unit must be '{unit}' for {usage_type}", 422)
    fields["unit"] = unit
    await _check_cost_rate_overlap(
        db,
        provider=fields["provider"],
        model_or_service=fields.get("model_or_service"),
        usage_type=usage_type,
        capability_key=fields.get("capability_key"),
        effective_from=fields["effective_from"],
        effective_until=fields.get("effective_until"),
    )
    rate = ProviderCostRate(created_by=actor.user_id, **fields)
    db.add(rate)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="pricing.cost_rate_created",
        target_type="cost_rate",
        target_id=rate.id,
        after={
            "provider": rate.provider,
            "model_or_service": rate.model_or_service,
            "usage_type": rate.usage_type,
            "unit_cost": str(rate.unit_cost),
            "currency": rate.currency,
        },
    )
    return rate


async def supersede_cost_rate(
    db: AsyncSession,
    rate: ProviderCostRate,
    *,
    effective_until: datetime,
    successor: dict,
    actor: Actor,
) -> ProviderCostRate:
    """Atomically close the old window and open the new one — the ONLY legal
    mutation of an existing cost rate."""
    if rate.effective_until is not None:
        raise AppError("COST_RATE_IMMUTABLE", "Rate is already superseded", 409)
    if effective_until <= rate.effective_from:
        raise AppError("VALIDATION_ERROR", "effective_until must be after effective_from", 422)
    rate.effective_until = effective_until
    await db.flush()
    successor.setdefault("provider", rate.provider)
    successor.setdefault("model_or_service", rate.model_or_service)
    successor.setdefault("usage_type", rate.usage_type)
    successor.setdefault("capability_key", rate.capability_key)
    successor.setdefault("currency", rate.currency)
    successor.setdefault("effective_from", effective_until)
    new_rate = await create_cost_rate(db, actor=actor, **successor)
    await record_audit(
        db,
        actor=actor,
        action="pricing.cost_rate_superseded",
        target_type="cost_rate",
        target_id=rate.id,
        after={"successor_id": new_rate.id},
    )
    return new_rate


async def create_price_policy(db: AsyncSession, *, actor: Actor, **fields) -> PricePolicy:
    validate_policy_params(fields["policy_type"], fields["params"])
    if fields.get("usage_type") is not None and fields["usage_type"] not in USAGE_TYPES:
        raise AppError("UNKNOWN_USAGE_TYPE", f"Unknown usage type '{fields['usage_type']}'", 422)
    scope_dims = [fields.get("tenant_id"), fields.get("partner_id"), fields.get("plan_version_id")]
    if sum(1 for d in scope_dims if d) > 1:
        raise AppError(
            "INVALID_POLICY_PARAMS", "At most one scope dimension (tenant/partner/plan)", 422
        )
    policy = PricePolicy(created_by=actor.user_id, **fields)
    db.add(policy)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="pricing.policy_created",
        target_type="price_policy",
        target_id=policy.id,
        tenant_id=policy.tenant_id,
        partner_id=policy.partner_id,
        after={"name": policy.name, "policy_type": policy.policy_type},
    )
    return policy


async def deactivate_price_policy(
    db: AsyncSession,
    policy: PricePolicy,
    *,
    effective_until: datetime | None,
    actor: Actor,
) -> PricePolicy:
    """The only legal mutation: turn it off (content is immutable)."""
    policy.is_active = False
    if effective_until is not None:
        policy.effective_until = effective_until
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="pricing.policy_deactivated",
        target_type="price_policy",
        target_id=policy.id,
        tenant_id=policy.tenant_id,
    )
    return policy


async def create_fx_rate(db: AsyncSession, *, actor: Actor, **fields) -> FxRate:
    base, quote = fields["base_currency"], fields["quote_currency"]
    if base == quote:
        raise AppError("FX_RATE_INVALID", "base and quote currencies must differ", 422)
    rate_val = Decimal(str(fields["rate"]))
    if not rate_val.is_finite() or rate_val <= 0:
        raise AppError("FX_RATE_INVALID", "rate must be a positive finite number", 422)
    # R61[1]: FX rates were PERMANENTLY immutable — an open-ended rate blocked
    # every future rate for the pair and no supersede path existed, so a pair,
    # once entered, could never track the market again. Mirror the cost-rate
    # supersede semantics: a live open-ended rate whose window started before
    # the new rate is auto-closed at the new effective_from (the only legal
    # mutation, audited). Point-in-time reads stay correct: old timestamps
    # still resolve the old rate; snapshots on rated rows are untouched.
    open_ended = (
        await db.execute(
            select(FxRate)
            .where(
                FxRate.base_currency == base,
                FxRate.quote_currency == quote,
                FxRate.effective_until.is_(None),
                FxRate.effective_from < fields["effective_from"],
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if open_ended is not None:
        open_ended.effective_until = fields["effective_from"]
        await db.flush()
        await record_audit(
            db,
            actor=actor,
            action="fx.rate_superseded",
            target_type="fx_rate",
            target_id=open_ended.id,
            after={"pair": f"{base}/{quote}", "closed_at": str(fields["effective_from"])},
        )
    conds = [
        FxRate.base_currency == base,
        FxRate.quote_currency == quote,
        or_(FxRate.effective_until.is_(None), FxRate.effective_until > fields["effective_from"]),
    ]
    if fields.get("effective_until") is not None:
        conds.append(FxRate.effective_from < fields["effective_until"])
    overlap = (
        await db.execute(select(FxRate.id).where(and_(*conds)).limit(1))
    ).scalar_one_or_none()
    if overlap is not None:
        raise AppError("FX_RATE_OVERLAP", "Overlapping window for this currency pair", 409)
    fx = FxRate(created_by=actor.user_id, **fields)
    db.add(fx)
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="fx.rate_created",
        target_type="fx_rate",
        target_id=fx.id,
        after={"pair": f"{base}/{quote}", "rate": str(fx.rate)},
    )
    # Unblock blocked ratings asynchronously
    enqueue(db, "fx.rate_created", {"fx_rate_id": fx.id})
    return fx
