"""Rating engine: cost resolution, sell-policy resolution, FX, snapshots
(ADR-014 §4.3). Consumes outbox usage.recorded; rate_pending() batch-scans."""

from datetime import UTC, datetime
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal

import structlog
from sqlalchemy import and_, or_, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.pricing import (
    FxRate,
    PricePolicy,
    ProviderCostRate,
    RatedUsage,
    minor_multiplier,
)
from app.controlplane.models.tenant import TenantAccount
from app.controlplane.models.usage import UsageEvent
from app.controlplane.worker import register_handler
from app.exceptions import AppError

log = structlog.get_logger()


# ── Pure computation helpers (unit-tested without DB) ────────


def apply_tiers(unit_cost: Decimal, tier_rules: list | None, quantity: Decimal) -> Decimal:
    """Highest min_qty <= |quantity| wins; per-event, no monthly accumulation (ADR).

    Tier selection uses the MAGNITUDE of quantity so a negative adjustment
    (reversal) is priced at the SAME tier the original event used — otherwise
    no tier matches a negative quantity (0 <= -N is False) and the reversal
    falls back to the base rate, over/under-crediting the tenant (R52[8])."""
    if not tier_rules:
        return unit_cost
    mag = abs(quantity)
    best = unit_cost
    best_min = Decimal("-1")
    for tier in tier_rules:
        try:
            min_qty = Decimal(str(tier.get("min_qty", "0")))
            tier_cost = Decimal(str(tier["unit_cost"]))
        except Exception:  # noqa: BLE001 — malformed tier ignored (validated at write)
            continue
        if min_qty <= mag and min_qty > best_min:
            best, best_min = tier_cost, min_qty
    return best


def compute_internal_cost_minor(
    unit_cost: Decimal,
    quantity: Decimal,
    currency: str,
    minimum_fee_minor: int | None,
) -> int:
    """Internal cost in `currency` minor units, sign-linear in quantity.

    Computed on the MAGNITUDE then re-signed so rating(-N) == -rating(+N) — a
    full reversal nets to zero (R52[7]). minimum_fee is a FLOOR on a real
    (positive) charge, so it applies to the magnitude only; clamping a negative
    reversal up to +minimum_fee would flip a credit into a charge."""
    sign = -1 if quantity < 0 else 1
    magnitude = abs(quantity)
    raw = (unit_cost * magnitude * minor_multiplier(currency)).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    )
    cost = int(raw)
    if minimum_fee_minor is not None and cost > 0:
        cost = max(cost, minimum_fee_minor)
    return sign * cost


def compute_billable_minor(
    policy_type: str,
    params: dict,
    *,
    internal_cost_minor: int,
    quantity: Decimal,
    prior_period_quantity: Decimal = Decimal(0),
    usage_metadata: dict | None = None,
) -> int:
    """Per-policy-type billable in the POLICY's currency (minor units)."""
    if params.get("exclude_failed") and (usage_metadata or {}).get("status") == "failed":
        return 0
    if policy_type == "cost_plus_percentage":
        pct = Decimal(str(params["percentage"]))
        return int(
            (Decimal(internal_cost_minor) * (1 + pct / 100)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
    if policy_type == "cost_plus_fixed":
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        # markup applies per STARTED block → ceiling on the MAGNITUDE, then
        # re-signed. A positive event of 1400 over per=1000 bills 2 blocks; a
        # reversal of -1400 reverses exactly 2 blocks (-2), so forward+reversal
        # nets to zero. The old max(units, 1) on a signed ceiling forced +1
        # block onto every refund (R52[9]).
        sign = -1 if quantity < 0 else 1
        blocks = int((abs(quantity) / per).to_integral_value(rounding=ROUND_CEILING))
        if blocks == 0 and quantity != 0:
            blocks = 1
        return internal_cost_minor + sign * int(params["fixed_markup_minor"]) * blocks
    if policy_type == "fixed_unit_price":
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        price = Decimal(int(params["unit_price_minor"]))
        return int((price * quantity / per).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if policy_type == "included_quota_then_overage":
        included = Decimal(str(params["included_quota"]))
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        price = Decimal(int(params["overage_unit_price_minor"]))
        already_over = max(prior_period_quantity - included, Decimal(0))
        total_over = max(prior_period_quantity + quantity - included, Decimal(0))
        billable_qty = total_over - already_over
        return int((price * billable_qty / per).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    raise AppError("INVALID_POLICY_PARAMS", f"Unknown policy type '{policy_type}'", 422)


def specificity_rank(
    policy: PricePolicy, *, tenant_id: str, partner_id: str | None, plan_version_id: str | None
) -> int | None:
    """Higher = more specific. None = policy does not apply to this tenant."""
    if policy.tenant_id is not None:
        return 3 if policy.tenant_id == tenant_id else None
    if policy.partner_id is not None:
        return 2 if (partner_id and policy.partner_id == partner_id) else None
    if policy.plan_version_id is not None:
        return 1 if (plan_version_id and policy.plan_version_id == plan_version_id) else None
    return 0  # global


# ── FX ───────────────────────────────────────────────────────


async def resolve_fx(
    db: AsyncSession, base: str, quote: str, at: datetime
) -> tuple[Decimal, dict] | None:
    """Rate + snapshot for 1 base = X quote at time `at`; inverse pairs are
    consulted as a fallback. None when no rate exists (caller blocks)."""
    if base == quote:
        return Decimal(1), {"identity": True}
    row = (
        await db.execute(
            select(FxRate)
            .where(
                FxRate.base_currency == base,
                FxRate.quote_currency == quote,
                FxRate.effective_from <= at,
                or_(FxRate.effective_until.is_(None), FxRate.effective_until > at),
            )
            .order_by(FxRate.effective_from.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if row is not None:
        return row.rate, {
            "fx_rate_id": row.id,
            "base": base,
            "quote": quote,
            "rate": str(row.rate),
            "effective_from": row.effective_from.isoformat(),
        }
    inverse = (
        await db.execute(
            select(FxRate)
            .where(
                FxRate.base_currency == quote,
                FxRate.quote_currency == base,
                FxRate.effective_from <= at,
                or_(FxRate.effective_until.is_(None), FxRate.effective_until > at),
            )
            .order_by(FxRate.effective_from.desc())
            .limit(1)
        )
    ).scalar_one_or_none()
    if inverse is not None and inverse.rate != 0:
        rate = (Decimal(1) / inverse.rate).quantize(Decimal("0.00000001"))
        return rate, {
            "fx_rate_id": inverse.id,
            "base": base,
            "quote": quote,
            "rate": str(rate),
            "inverse_of": str(inverse.rate),
            "effective_from": inverse.effective_from.isoformat(),
        }
    return None


def convert_minor(amount_minor: int, rate: Decimal, from_cur: str, to_cur: str) -> int:
    """Convert minor units across currencies with differing minor multipliers."""
    major = Decimal(amount_minor) / minor_multiplier(from_cur)
    return int(
        (major * rate * minor_multiplier(to_cur)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def convert_exact(amount_exact: Decimal, rate: Decimal, from_cur: str, to_cur: str) -> Decimal:
    """FX-convert an EXACT fractional minor amount without rounding (R75).

    Same math as convert_minor but keeps full Decimal precision so the invoice
    can round the SUM once instead of each converted event."""
    major = amount_exact / minor_multiplier(from_cur)
    return major * rate * minor_multiplier(to_cur)


def compute_internal_cost_exact(
    unit_cost: Decimal, quantity: Decimal, currency: str, minimum_fee_minor: int | None
) -> Decimal:
    """Unrounded internal cost in `currency` minor units (R75). Mirrors
    compute_internal_cost_minor's sign/minimum-fee handling but does not
    quantize — the per-event remainder is preserved so charging rounds the
    accumulated sum once."""
    sign = Decimal(-1) if quantity < 0 else Decimal(1)
    magnitude = abs(quantity)
    raw = unit_cost * magnitude * minor_multiplier(currency)
    if minimum_fee_minor is not None and raw > 0:
        raw = max(raw, Decimal(minimum_fee_minor))
    return sign * raw


def compute_billable_exact(
    policy_type: str,
    params: dict,
    *,
    internal_cost_exact: Decimal,
    quantity: Decimal,
    prior_period_quantity: Decimal = Decimal(0),
    usage_metadata: dict | None = None,
) -> Decimal:
    """Unrounded per-event billable in the POLICY's currency (R75).

    Mirrors compute_billable_minor exactly, minus the per-event quantize — a
    fixed_unit_price of $1/1M tokens on a 4000-token event yields Decimal('0.4')
    here (accumulated), not 0 (rounded away per event). cost_plus_fixed's block
    markup is inherently integer, so only its internal-cost component carries a
    fraction."""
    if params.get("exclude_failed") and (usage_metadata or {}).get("status") == "failed":
        return Decimal(0)
    if policy_type == "cost_plus_percentage":
        pct = Decimal(str(params["percentage"]))
        return internal_cost_exact * (1 + pct / 100)
    if policy_type == "cost_plus_fixed":
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        sign = Decimal(-1) if quantity < 0 else Decimal(1)
        blocks = int((abs(quantity) / per).to_integral_value(rounding=ROUND_CEILING))
        if blocks == 0 and quantity != 0:
            blocks = 1
        return internal_cost_exact + sign * Decimal(int(params["fixed_markup_minor"])) * blocks
    if policy_type == "fixed_unit_price":
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        price = Decimal(int(params["unit_price_minor"]))
        return price * quantity / per
    if policy_type == "included_quota_then_overage":
        included = Decimal(str(params["included_quota"]))
        per = Decimal(str(params.get("per_quantity", "1")))
        if per <= 0:
            raise AppError("INVALID_POLICY_PARAMS", "per_quantity must be positive", 422)
        price = Decimal(int(params["overage_unit_price_minor"]))
        already_over = max(prior_period_quantity - included, Decimal(0))
        total_over = max(prior_period_quantity + quantity - included, Decimal(0))
        billable_qty = total_over - already_over
        return price * billable_qty / per
    raise AppError("INVALID_POLICY_PARAMS", f"Unknown policy type '{policy_type}'", 422)


# ── Resolution ───────────────────────────────────────────────


async def _resolve_cost_rate(
    db: AsyncSession, event: UsageEvent
) -> tuple[ProviderCostRate | None, dict]:
    """Ladder: exact → provider wildcard → capability-level → offering
    fallback → no_rate. Returns (rate_row|None, snapshot)."""
    at = event.occurred_at
    window = and_(
        ProviderCostRate.effective_from <= at,
        or_(
            ProviderCostRate.effective_until.is_(None),
            ProviderCostRate.effective_until > at,
        ),
    )

    def snap(rate: ProviderCostRate, note: str | None = None) -> dict:
        s = {
            "cost_rate_id": rate.id,
            "provider": rate.provider,
            "model_or_service": rate.model_or_service,
            "usage_type": rate.usage_type,
            "unit": rate.unit,
            "currency": rate.currency,
            "unit_cost": str(rate.unit_cost),
            "tier_rules": rate.tier_rules,
            "minimum_fee_minor": rate.minimum_fee_minor,
            "effective_from": rate.effective_from.isoformat(),
        }
        if note:
            s["resolution"] = note
        return s

    if event.provider and event.model_or_service:
        exact = (
            await db.execute(
                select(ProviderCostRate)
                .where(
                    ProviderCostRate.provider == event.provider,
                    ProviderCostRate.model_or_service == event.model_or_service,
                    ProviderCostRate.usage_type == event.usage_type,
                    window,
                )
                .order_by(ProviderCostRate.effective_from.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if exact is not None:
            return exact, snap(exact, "exact")
    if event.provider:
        wildcard = (
            await db.execute(
                select(ProviderCostRate)
                .where(
                    ProviderCostRate.provider == event.provider,
                    ProviderCostRate.model_or_service.is_(None),
                    ProviderCostRate.usage_type == event.usage_type,
                    window,
                )
                .order_by(ProviderCostRate.effective_from.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if wildcard is not None:
            return wildcard, snap(wildcard, "provider_wildcard")
    # Capability-level fallback: a provider-agnostic rate for this usage_type.
    # Constrain to the event's OWN provider so an unrelated provider's
    # capability rate can't price this event (R52[11]); a NULL-provider
    # capability rate remains a legitimate cross-provider default. Deterministic
    # tie-break on id keeps replays stable when two rates share effective_from.
    capability = (
        await db.execute(
            select(ProviderCostRate)
            .where(
                ProviderCostRate.capability_key.is_not(None),
                ProviderCostRate.usage_type == event.usage_type,
                or_(
                    ProviderCostRate.provider == event.provider,
                    ProviderCostRate.provider.is_(None),
                ),
                window,
            )
            .order_by(
                ProviderCostRate.effective_from.desc(),
                ProviderCostRate.id.desc(),
            )
            .limit(1)
        )
    ).scalar_one_or_none()
    if capability is not None:
        return capability, snap(capability, "capability")
    # Offering fallback (workflow provider steps carry offering cost)
    if event.workflow_run_id and event.provider_connection_id:
        from app.models.provider import ProviderModelOffering

        offering = (
            await db.execute(
                select(ProviderModelOffering)
                .where(
                    ProviderModelOffering.connection_id == event.provider_connection_id,
                    ProviderModelOffering.model_name == (event.model_or_service or ""),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if offering is not None and offering.cost_per_call_usd is not None:
            return None, {
                "fallback": "offering",
                "offering_id": offering.id,
                "currency": "USD",
                "unit_cost": str(offering.cost_per_call_usd),
                "resolution": "offering_fallback",
            }
    return None, {"no_rate": True, "currency": settings.platform_currency}


async def _resolve_sell_policy(
    db: AsyncSession, event: UsageEvent, tenant: TenantAccount
) -> PricePolicy | None:
    """tenant > partner > plan > global; then priority DESC, effective_from
    DESC, id DESC (deterministic)."""
    at = event.occurred_at
    plan_version_id = None
    try:
        from app.controlplane.models.billing import Subscription

        sub = (
            await db.execute(
                select(Subscription.plan_version_id)
                .where(
                    Subscription.tenant_id == tenant.id,
                    Subscription.status.in_(
                        ["trial", "active", "past_due", "cancel_at_period_end"]
                    ),
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        plan_version_id = sub
    except ImportError:  # billing lands in P6
        pass

    candidates = (
        (
            await db.execute(
                select(PricePolicy).where(
                    PricePolicy.is_active.is_(True),
                    PricePolicy.effective_from <= at,
                    or_(
                        PricePolicy.effective_until.is_(None),
                        PricePolicy.effective_until > at,
                    ),
                    or_(
                        PricePolicy.usage_type == event.usage_type,
                        PricePolicy.usage_type.is_(None),
                    ),
                )
            )
        )
        .scalars()
        .all()
    )
    best: tuple[int, int, datetime, str] | None = None
    best_policy: PricePolicy | None = None
    for p in candidates:
        rank = specificity_rank(
            p,
            tenant_id=tenant.id,
            partner_id=tenant.partner_id,
            plan_version_id=plan_version_id,
        )
        if rank is None:
            continue
        # usage_type exact beats NULL wildcard within the same rank tier
        type_rank = 1 if p.usage_type is not None else 0
        key = (rank, type_rank, p.priority, p.effective_from, p.id)
        if best is None or key > best:
            best, best_policy = key, p
    return best_policy


# ── Rating ───────────────────────────────────────────────────


async def rate_event(db: AsyncSession, usage_event_id: str) -> RatedUsage | None:
    """Rate one event. Idempotent (unique usage_event_id, ON CONFLICT skip)."""
    event = await db.get(UsageEvent, usage_event_id)
    if event is None:
        return None
    existing = (
        await db.execute(
            select(RatedUsage).where(RatedUsage.usage_event_id == usage_event_id).limit(1)
        )
    ).scalar_one_or_none()
    if existing is not None and existing.status != "blocked":
        return existing
    # existing blocked row → retry FX resolution below, updating in place
    tenant = await db.get(TenantAccount, event.tenant_id)
    if tenant is None:
        return None

    # 1. Cost
    rate_row, cost_snapshot = await _resolve_cost_rate(db, event)
    cost_currency = cost_snapshot.get("currency", settings.platform_currency)
    if rate_row is not None:
        unit_cost = apply_tiers(rate_row.unit_cost, rate_row.tier_rules, event.quantity)
        cost_snapshot["tier_applied_unit_cost"] = str(unit_cost)
        internal_cost = compute_internal_cost_minor(
            unit_cost, event.quantity, cost_currency, rate_row.minimum_fee_minor
        )
        internal_cost_exact = compute_internal_cost_exact(
            unit_cost, event.quantity, cost_currency, rate_row.minimum_fee_minor
        )
    elif "unit_cost" in cost_snapshot:  # offering fallback
        internal_cost = compute_internal_cost_minor(
            Decimal(cost_snapshot["unit_cost"]), Decimal(1), cost_currency, None
        )
        internal_cost_exact = compute_internal_cost_exact(
            Decimal(cost_snapshot["unit_cost"]), Decimal(1), cost_currency, None
        )
    else:  # no_rate
        internal_cost = 0
        internal_cost_exact = Decimal(0)

    # 2. Sell policy
    policy = await _resolve_sell_policy(db, event, tenant)
    prior_qty = Decimal(0)
    if policy is not None and policy.policy_type == "included_quota_then_overage":
        # Period accumulation: tenant-tz calendar month of occurred_at
        from zoneinfo import ZoneInfo

        try:
            tz = ZoneInfo(tenant.timezone)
        except Exception:  # noqa: BLE001
            tz = UTC
        local = event.occurred_at.astimezone(tz)
        month_start = local.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from sqlalchemy import func as _f

        # "Prior" = everything in the period that logically precedes THIS event.
        # Order by (occurred_at, created_at, id): a reversal adjustment shares
        # the original's occurred_at but is created later, so ordering by
        # created_at includes the original in prior_qty — without which the
        # reversal always netted to 0 overage (R52[10], strict occurred_at<
        # excluded the same-timestamp original).
        precedes = or_(
            UsageEvent.occurred_at < event.occurred_at,
            and_(
                UsageEvent.occurred_at == event.occurred_at,
                or_(
                    UsageEvent.created_at < event.created_at,
                    and_(
                        UsageEvent.created_at == event.created_at,
                        UsageEvent.id < event.id,
                    ),
                ),
            ),
        )
        q = (
            select(_f.coalesce(_f.sum(UsageEvent.quantity), 0))
            .select_from(UsageEvent)
            .outerjoin(RatedUsage, RatedUsage.usage_event_id == UsageEvent.id)
            .where(
                UsageEvent.tenant_id == tenant.id,
                UsageEvent.usage_type == event.usage_type,
                UsageEvent.occurred_at >= month_start,
                precedes,
                # A voided rating means the event was struck from billing — it
                # must not consume the included quota either (R52[13]).
                or_(RatedUsage.id.is_(None), RatedUsage.status != "voided"),
            )
        )
        # Failed events that the policy excludes from billing shouldn't consume
        # the included quota either, else a burst of billed-0 failures silently
        # pushes real usage into overage (R52[13]).
        if policy.params.get("exclude_failed"):
            q = q.where(
                or_(
                    UsageEvent.metadata_["status"].astext.is_(None),
                    UsageEvent.metadata_["status"].astext != "failed",
                )
            )
        prior_qty = Decimal((await db.execute(q)).scalar_one())

    # Currency normalization + margin (platform currency). Do FX gap-collection
    # up front because cost_plus_* policies need internal_cost expressed in the
    # POLICY currency BEFORE computing billable (R52[6] CRITICAL: internal_cost
    # is in the COST rate's currency; deriving billable from it yields a number
    # in cost-currency minor units, but the downstream conversion treats it as
    # policy currency and only bridges policy->tenant, never cost->policy).
    fx_snapshot: dict | None = None
    blocked_gaps: list[str] = []

    if policy is not None:
        policy_currency = policy.currency
        cost_for_billing = internal_cost
        cost_for_billing_exact = internal_cost_exact
        # cost_plus_* derive billable from internal cost → that input must be in
        # the policy's currency. fixed_unit_price / included_quota price in the
        # policy currency directly and ignore internal_cost, so no bridge needed.
        if (
            policy.policy_type in ("cost_plus_percentage", "cost_plus_fixed")
            and internal_cost != 0
            and cost_currency != policy_currency
        ):
            fx_cp = await resolve_fx(db, cost_currency, policy_currency, event.occurred_at)
            if fx_cp is None:
                blocked_gaps.append(f"{cost_currency}->{policy_currency}")
                cost_for_billing = 0
                cost_for_billing_exact = Decimal(0)
            else:
                cost_for_billing = convert_minor(
                    internal_cost, fx_cp[0], cost_currency, policy_currency
                )
                cost_for_billing_exact = convert_exact(
                    internal_cost_exact, fx_cp[0], cost_currency, policy_currency
                )
        billable_policy_ccy = compute_billable_minor(
            policy.policy_type,
            policy.params,
            internal_cost_minor=cost_for_billing,
            quantity=event.quantity,
            prior_period_quantity=prior_qty,
            usage_metadata=event.metadata_,
        )
        billable_policy_exact = compute_billable_exact(
            policy.policy_type,
            policy.params,
            internal_cost_exact=cost_for_billing_exact,
            quantity=event.quantity,
            prior_period_quantity=prior_qty,
            usage_metadata=event.metadata_,
        )
        sell_snapshot = {
            "price_policy_id": policy.id,
            "name": policy.name,
            "policy_type": policy.policy_type,
            "scope": (
                "tenant"
                if policy.tenant_id
                else "partner"
                if policy.partner_id
                else "plan_version"
                if policy.plan_version_id
                else "global"
            ),
            "params": policy.params,
            "currency": policy.currency,
        }
    else:
        billable_policy_ccy = 0
        billable_policy_exact = Decimal(0)
        sell_snapshot = {"no_policy": True, "currency": tenant.currency}
        policy_currency = tenant.currency
        log.warning("cp_rating_no_policy", usage_event_id=event.id, tenant_id=tenant.id)

    # 3. Convert billable from policy currency → tenant currency (both the
    # rounded and EXACT columns — R75: the exact column is summed and rounded
    # once at invoice time to avoid per-event rounding to 0).
    billable_minor = billable_policy_ccy
    billable_exact = billable_policy_exact
    if policy_currency != tenant.currency:
        fx = await resolve_fx(db, policy_currency, tenant.currency, event.occurred_at)
        if fx is None:
            blocked_gaps.append(f"{policy_currency}->{tenant.currency}")
        else:
            rate, fx_snapshot = fx
            billable_minor = convert_minor(
                billable_policy_ccy, rate, policy_currency, tenant.currency
            )
            billable_exact = convert_exact(
                billable_policy_exact, rate, policy_currency, tenant.currency
            )

    margin: int | None = None
    if not blocked_gaps:
        pc = settings.platform_currency
        billable_pc = cost_pc = None
        fx_b = await resolve_fx(db, tenant.currency, pc, event.occurred_at)
        fx_c = await resolve_fx(db, cost_currency, pc, event.occurred_at)
        if fx_b is not None and fx_c is not None:
            billable_pc = convert_minor(billable_minor, fx_b[0], tenant.currency, pc)
            cost_pc = convert_minor(internal_cost, fx_c[0], cost_currency, pc)
            margin = billable_pc - cost_pc
        # Missing margin-side FX does NOT block billing — margin stays NULL.

    status = "blocked" if blocked_gaps else "rated"
    values = dict(
        usage_event_id=event.id,
        tenant_id=tenant.id,
        org_id=event.org_id,
        usage_type=event.usage_type,
        quantity=event.quantity,
        cost_rate_id=rate_row.id if rate_row else None,
        cost_rate_snapshot=cost_snapshot,
        internal_cost_minor=internal_cost,
        # Exact cost is in the SAME currency as internal_cost_minor
        # (internal_cost_currency) — parallel to the rounded column.
        internal_cost_exact=Decimal(0) if blocked_gaps else internal_cost_exact,
        internal_cost_currency=cost_currency,
        price_policy_id=policy.id if policy else None,
        sell_rate_snapshot=(
            {**sell_snapshot, "fx_gaps": blocked_gaps} if blocked_gaps else sell_snapshot
        ),
        billable_amount_minor=0 if blocked_gaps else billable_minor,
        billable_amount_exact=Decimal(0) if blocked_gaps else billable_exact,
        billable_currency=tenant.currency,
        fx_rate_snapshot=fx_snapshot,
        margin_minor=margin,
        status=status,
    )
    if existing is not None:  # unblocking retry — update the blocked row in place
        for k, v in values.items():
            setattr(existing, k, v)
        existing.rated_at = datetime.now(UTC)
        await db.flush()
        return existing
    from ulid import ULID

    stmt = (
        pg_insert(RatedUsage)
        .values(id=str(ULID()), **values)
        .on_conflict_do_nothing(index_elements=["usage_event_id"])
        .returning(RatedUsage.id)
    )
    inserted = (await db.execute(stmt)).scalar_one_or_none()
    if inserted is None:
        return (
            await db.execute(select(RatedUsage).where(RatedUsage.usage_event_id == usage_event_id))
        ).scalar_one()  # concurrent rater won
    return await db.get(RatedUsage, inserted)


async def rate_pending(db: AsyncSession, tenant_id: str | None = None, limit: int = 500) -> int:
    """Batch: rate unrated events + retry blocked rows."""
    q = (
        select(UsageEvent.id)
        .outerjoin(RatedUsage, RatedUsage.usage_event_id == UsageEvent.id)
        .where(or_(RatedUsage.id.is_(None), RatedUsage.status == "blocked"))
        .order_by(UsageEvent.occurred_at)
        .limit(limit)
    )
    if tenant_id:
        q = q.where(UsageEvent.tenant_id == tenant_id)
    ids = (await db.execute(q)).scalars().all()
    count = 0
    for event_id in ids:
        rated = await rate_event(db, event_id)
        if rated is not None and rated.status != "blocked":
            count += 1
    return count


async def void_rated(db: AsyncSession, rated_id: str, *, reason: str, actor) -> RatedUsage:
    from app.controlplane.services.audit import record_audit

    row = await db.get(RatedUsage, rated_id)
    if row is None:
        raise AppError("RATING_NOT_FOUND", "Rated usage not found", 404)
    if row.status == "invoiced":
        raise AppError("RATED_USAGE_INVOICED", "Cannot void an invoiced rating", 409)
    row.status = "voided"
    row.void_reason = reason
    await record_audit(
        db,
        actor=actor,
        action="rated_usage.voided",
        target_type="rated_usage",
        target_id=row.id,
        tenant_id=row.tenant_id,
        reason=reason,
    )
    await db.flush()
    return row


# ── Outbox handlers ──────────────────────────────────────────


@register_handler("usage.recorded")
async def _handle_usage_recorded(db: AsyncSession, payload: dict) -> None:
    await rate_event(db, payload["usage_event_id"])


@register_handler("fx.rate_created")
async def _handle_fx_created(db: AsyncSession, payload: dict) -> None:
    """Retry blocked ratings once a new rate lands."""
    blocked = (
        (
            await db.execute(
                select(RatedUsage.usage_event_id).where(RatedUsage.status == "blocked").limit(500)
            )
        )
        .scalars()
        .all()
    )
    for event_id in blocked:
        await rate_event(db, event_id)
