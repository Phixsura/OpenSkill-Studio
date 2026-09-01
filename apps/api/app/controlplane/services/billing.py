"""Subscription lifecycle, proration, invoice generation, webhook processing
(ADR-014 §6.3–6.5)."""

from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

import structlog
from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.billing import (
    BillingPeriod,
    BillingWebhookEvent,
    CreditNote,
    Invoice,
    InvoiceLine,
    InvoiceSequence,
    PaymentRecord,
    Subscription,
    SubscriptionChange,
)
from app.controlplane.models.outbox import enqueue
from app.controlplane.models.plan import PlanPrice, PlanVersion, ProductPlan
from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import credits as credit_svc
from app.controlplane.services.audit import SYSTEM_ACTOR, Actor, record_audit
from app.controlplane.services.entitlements import invalidate_cache
from app.controlplane.worker import register_handler
from app.exceptions import AppError

log = structlog.get_logger()


def _now() -> datetime:
    return datetime.now(UTC)


def _is_leap(year: int) -> bool:
    """Proper Gregorian rule — 2100 is NOT a leap year (÷100 but not ÷400)."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def _add_interval(start: datetime, interval: str) -> datetime:
    if interval == "year":
        # start.replace(year=+1) raises on Feb 29 (no Feb 29 next year) → 500
        # at subscription start and a poisoned period.close_due at rollover.
        # Clamp the day to the target month's length, mirroring the month path.
        target_year = start.year + 1
        max_day = (
            29
            if (start.month == 2 and _is_leap(target_year))
            else _month_len(target_year, start.month)
        )
        return start.replace(year=target_year, day=min(start.day, max_day))
    # month arithmetic without external deps
    year = start.year + (start.month == 12)
    month = (start.month % 12) + 1
    day = min(start.day, _month_len(year, month))
    return start.replace(year=year, month=month, day=day)


def _month_len(year: int, month: int) -> int:
    return [31, 29 if _is_leap(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1]


# ── Proration (pure, unit-tested; ADR-014 §6.3) ──────────────


def proration_preview(
    *,
    period_start: datetime,
    period_end: datetime,
    at: datetime,
    old_amount_minor: int,
    new_amount_minor: int,
    old_seats: int = 0,
    new_seats: int = 0,
    seat_price_minor: int = 0,
) -> dict:
    """Per-day segment walk. Upgrade = immediate; the preview returns the
    credit for the unused old plan + charge for the remaining new plan."""
    total_days = max((period_end - period_start).days, 1)
    used_days = max(min((at - period_start).days, total_days), 0)
    days_left = total_days - used_days

    def per_day(amount: int) -> Decimal:
        return Decimal(amount) / Decimal(total_days)

    credit_unused_old = int(
        (per_day(old_amount_minor) * days_left).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    charge_new_remaining = int(
        (per_day(new_amount_minor) * days_left).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    seat_delta = (new_seats - old_seats) * seat_price_minor
    seat_proration = int(
        (per_day(max(seat_delta, 0)) * days_left).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )
    net = charge_new_remaining - credit_unused_old + seat_proration
    return {
        "total_days": total_days,
        "days_left": days_left,
        "credit_unused_old_minor": credit_unused_old,
        "charge_new_remaining_minor": charge_new_remaining,
        "seat_proration_minor": seat_proration,
        "net_minor": net,
        "mode": "immediate" if net >= 0 else "next_period_default",
    }


# ── Subscription lifecycle ───────────────────────────────────


async def _resolve_plan_price(
    db: AsyncSession, plan_key: str, currency: str, interval: str
) -> tuple[PlanVersion, PlanPrice]:
    row = (
        await db.execute(
            select(PlanVersion, PlanPrice)
            .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
            .join(PlanPrice, PlanPrice.plan_version_id == PlanVersion.id)
            .where(
                ProductPlan.key == plan_key,
                ProductPlan.is_active.is_(True),
                PlanVersion.status == "active",
                PlanPrice.currency == currency,
                PlanPrice.interval == interval,
            )
            .limit(1)
        )
    ).one_or_none()
    if row is None:
        raise AppError(
            "PLAN_NOT_AVAILABLE",
            f"Plan '{plan_key}' has no active {interval} price in {currency}",
            404,
        )
    return row


async def get_live_subscription(db: AsyncSession, tenant_id: str) -> Subscription | None:
    return (
        await db.execute(
            select(Subscription)
            .where(Subscription.tenant_id == tenant_id, Subscription.status != "cancelled")
            .limit(1)
        )
    ).scalar_one_or_none()


async def start_subscription(
    db: AsyncSession,
    tenant: TenantAccount,
    *,
    plan_key: str,
    interval: str,
    seats: int,
    provider: str,
    actor: Actor,
) -> tuple[Subscription | None, str | None]:
    """Returns (subscription, checkout_url). Manual → immediate active;
    mock/stripe → pending checkout (webhook completes activation)."""
    if await get_live_subscription(db, tenant.id) is not None:
        raise AppError("SUBSCRIPTION_EXISTS", "Tenant already has a live subscription", 409)
    version, price = await _resolve_plan_price(db, plan_key, tenant.currency, interval)

    if provider == "manual":
        now = _now()
        sub = Subscription(
            tenant_id=tenant.id,
            plan_version_id=version.id,
            status="active",
            currency=tenant.currency,
            interval=interval,
            seat_quantity=seats,
            current_period_start=now,
            current_period_end=_add_interval(now, interval),
            provider=provider,
            created_by=actor.user_id,
        )
        db.add(sub)
        await db.flush()
        db.add(
            BillingPeriod(
                tenant_id=tenant.id,
                subscription_id=sub.id,
                period_start=sub.current_period_start,
                period_end=sub.current_period_end,
            )
        )
        if tenant.status == TenantStatus.TRIAL:
            from app.controlplane.services.tenants import transition_status

            await transition_status(db, tenant, TenantStatus.ACTIVE, actor=actor)
        await invalidate_cache(tenant.id)
        return sub, None

    from app.controlplane.services.billing_providers import get_billing_provider

    adapter = get_billing_provider(provider)
    if adapter is None:
        raise AppError("VALIDATION_ERROR", f"Unknown billing provider '{provider}'", 422)
    session = await adapter.create_checkout_session(
        tenant=tenant,
        kind="subscription",
        plan_price=price,
        currency=tenant.currency,
        success_url=f"{settings.frontend_url}/dashboard/tenant/{tenant.id}/billing?ok=1",
        cancel_url=f"{settings.frontend_url}/dashboard/tenant/{tenant.id}/billing?cancelled=1",
        metadata={"plan_key": plan_key, "interval": interval, "seats": str(seats)},
    )
    return None, session.url


async def activate_subscription_from_checkout(
    db: AsyncSession,
    tenant: TenantAccount,
    *,
    plan_key: str,
    interval: str,
    seats: int,
    provider: str,
    external_customer_ref: str | None,
    external_ref: str | None,
) -> Subscription:
    """Webhook completion path — guarded against duplicates by the caller's
    webhook-event unique key + the live-subscription partial index."""
    existing = await get_live_subscription(db, tenant.id)
    if existing is not None:
        # R64[17]: a second completed checkout session (double-click, two tabs)
        # creates a REAL second recurring subscription at the provider with no
        # platform record — silently double-billing the customer forever.
        # Cancel the orphan provider-side; the platform keeps the first.
        if (
            external_ref
            and external_ref != existing.external_ref
            and provider in ("mock", "stripe")
        ):
            from app.controlplane.services.billing_providers import get_billing_provider

            adapter = get_billing_provider(provider)
            if adapter is not None:
                try:
                    await adapter.cancel_subscription(external_ref, at_period_end=False)
                    log.warning(
                        "cp_orphan_subscription_cancelled",
                        tenant_id=tenant.id,
                        orphan_ref=external_ref,
                        kept_ref=existing.external_ref,
                    )
                except Exception:  # noqa: BLE001 — orphan cleanup is best-effort
                    log.error(
                        "cp_orphan_subscription_cancel_failed",
                        tenant_id=tenant.id,
                        orphan_ref=external_ref,
                    )
        return existing
    version, _price = await _resolve_plan_price(db, plan_key, tenant.currency, interval)
    now = _now()
    sub = Subscription(
        tenant_id=tenant.id,
        plan_version_id=version.id,
        status="active",
        currency=tenant.currency,
        interval=interval,
        seat_quantity=seats,
        current_period_start=now,
        current_period_end=_add_interval(now, interval),
        provider=provider,
        external_customer_ref=external_customer_ref,
        external_ref=external_ref,
    )
    db.add(sub)
    await db.flush()
    db.add(
        BillingPeriod(
            tenant_id=tenant.id,
            subscription_id=sub.id,
            period_start=sub.current_period_start,
            period_end=sub.current_period_end,
        )
    )
    if tenant.status == TenantStatus.TRIAL:
        from app.controlplane.services.tenants import transition_status

        await transition_status(db, tenant, TenantStatus.ACTIVE, actor=SYSTEM_ACTOR)
    await invalidate_cache(tenant.id)
    return sub


async def change_plan(
    db: AsyncSession,
    tenant: TenantAccount,
    sub: Subscription,
    *,
    plan_key: str | None,
    seats: int | None,
    proration_mode: str | None,
    actor: Actor,
) -> dict:
    """Plan/seat change. Upgrades default immediate (entitlements now, net on
    next invoice); downgrades default next_period."""
    old_version = await db.get(PlanVersion, sub.plan_version_id)
    old_price = (
        await db.execute(
            select(PlanPrice).where(
                PlanPrice.plan_version_id == old_version.id,
                PlanPrice.currency == sub.currency,
                PlanPrice.interval == sub.interval,
            )
        )
    ).scalar_one_or_none()
    new_version, new_price = (
        await _resolve_plan_price(db, plan_key, sub.currency, sub.interval)
        if plan_key
        else (old_version, old_price)
    )
    new_seats = seats if seats is not None else sub.seat_quantity
    upgrade = (new_price.amount_minor if new_price else 0) >= (
        old_price.amount_minor if old_price else 0
    )
    mode = proration_mode or ("immediate" if upgrade else "next_period")
    preview = proration_preview(
        period_start=sub.current_period_start,
        period_end=sub.current_period_end,
        at=_now(),
        old_amount_minor=old_price.amount_minor if old_price else 0,
        new_amount_minor=new_price.amount_minor if new_price else 0,
        old_seats=sub.seat_quantity,
        new_seats=new_seats,
        seat_price_minor=(new_price.overage_seat_amount_minor or 0) if new_price else 0,
    )
    db.add(
        SubscriptionChange(
            subscription_id=sub.id,
            change_type="plan_change" if plan_key else "seat_change",
            from_plan_version_id=sub.plan_version_id,
            to_plan_version_id=new_version.id,
            from_seats=sub.seat_quantity,
            to_seats=new_seats,
            effective_at=_now() if mode == "immediate" else sub.current_period_end,
            proration_mode=mode,
            created_by=actor.user_id,
        )
    )
    if mode == "immediate":
        sub.plan_version_id = new_version.id
        sub.seat_quantity = new_seats
        # R64[16]: for provider-owned recurring billing (mock/stripe), the
        # change must be pushed to the provider or it keeps invoicing the OLD
        # price/quantity forever. Platform-side proration stays authoritative
        # (the adapter disables provider proration).
        if sub.provider in ("mock", "stripe") and sub.external_ref:
            from app.controlplane.services.billing_providers import get_billing_provider

            adapter = get_billing_provider(sub.provider)
            if adapter is not None and new_price is not None:
                if sub.provider == "stripe" and not new_price.external_price_ref:
                    raise AppError(
                        "PLAN_NOT_AVAILABLE",
                        "Target plan price has no Stripe price configured",
                        409,
                    )
                await adapter.change_subscription(
                    sub.external_ref,
                    new_price.external_price_ref or "",
                    new_seats,
                )
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="subscription.plan_changed",
        target_type="subscription",
        target_id=sub.id,
        tenant_id=tenant.id,
        before={"plan_version_id": old_version.id, "seats": sub.seat_quantity},
        after={"plan_version_id": new_version.id, "seats": new_seats, "mode": mode},
    )
    await invalidate_cache(tenant.id)
    return {"proration": preview, "mode": mode}


async def cancel_subscription(
    db: AsyncSession,
    tenant: TenantAccount,
    sub: Subscription,
    *,
    at_period_end: bool,
    actor: Actor,
) -> Subscription:
    if at_period_end:
        # R73[5]: include past_due — a dunning tenant must be able to schedule
        # non-renewal (they got 409 and kept accruing). 'trial' stays for
        # forward-compat even though no current path creates that status.
        result = await db.execute(
            update(Subscription)
            .where(
                Subscription.id == sub.id,
                Subscription.status.in_(["trial", "active", "past_due"]),
            )
            .values(status="cancel_at_period_end", cancel_at_period_end=True)
        )
    else:
        result = await db.execute(
            update(Subscription)
            .where(Subscription.id == sub.id, Subscription.status != "cancelled")
            .values(status="cancelled", cancelled_at=_now())
        )
    if not result.rowcount:
        raise AppError("SUBSCRIPTION_STATUS_CONFLICT", "Subscription state changed", 409)
    db.add(
        SubscriptionChange(
            subscription_id=sub.id,
            change_type="cancel",
            effective_at=sub.current_period_end if at_period_end else _now(),
            proration_mode="next_period",
            created_by=actor.user_id,
        )
    )
    if not at_period_end:
        # R41[4]: an immediate cancel flips status to 'cancelled', which
        # scan_due_periods no longer selects (it only scans active /
        # cancel_at_period_end / past_due). The current open period — holding
        # the final partial plan fee, any un-invoiced immediate-change proration,
        # and in-period rated usage — would otherwise never be closed or billed.
        # Enqueue a close for it now so the final invoice is generated. Truncate
        # the period to end now so the arrears plan/usage reflect only the used
        # portion, and force the sub row to be visible to the handler by leaving
        # the period selectable directly (the handler loads by id, not status).
        open_period = (
            await db.execute(
                select(BillingPeriod).where(
                    BillingPeriod.subscription_id == sub.id,
                    BillingPeriod.status == "open",
                )
            )
        ).scalar_one_or_none()
        if open_period is not None:
            now = _now()
            if open_period.period_end > now:
                open_period.period_end = now
            await db.flush()
            enqueue(db, "period.close_due", {"billing_period_id": open_period.id})
    if sub.provider in ("mock", "stripe") and sub.external_ref:
        from app.controlplane.services.billing_providers import get_billing_provider

        adapter = get_billing_provider(sub.provider)
        if adapter is not None:
            await adapter.cancel_subscription(sub.external_ref, at_period_end)
    await invalidate_cache(tenant.id)
    await db.refresh(sub)
    return sub


# ── Invoice generation (ADR-014 §6.4) ────────────────────────


async def _next_invoice_number(db: AsyncSession) -> str:
    year = str(_now().year)
    await db.execute(
        __import__("sqlalchemy.dialects.postgresql", fromlist=["insert"])
        .insert(InvoiceSequence)
        .values(scope=year, last_value=0)
        .on_conflict_do_nothing(index_elements=["scope"])
    )
    seq = (
        await db.execute(
            select(InvoiceSequence).where(InvoiceSequence.scope == year).with_for_update()
        )
    ).scalar_one()
    seq.last_value += 1
    return f"INV-{year}-{seq.last_value:06d}"


async def close_period_and_invoice(db: AsyncSession, period_id: str) -> Invoice | None:
    """Guarded period close → draft invoice with all line types → finalize.
    Idempotent: the open→closed transition is the gate."""
    period = await db.get(BillingPeriod, period_id)
    if period is None:
        return None
    result = await db.execute(
        update(BillingPeriod)
        .where(BillingPeriod.id == period_id, BillingPeriod.status == "open")
        .values(status="closed", closed_at=_now())
    )
    if not result.rowcount:
        return None  # already closed/invoiced by a concurrent worker
    sub = await db.get(Subscription, period.subscription_id)
    tenant = await db.get(TenantAccount, period.tenant_id)

    # R41[1]/[2]: bill this closed period in arrears on the plan/seats that were
    # in effect at its START, then let the proration lines below charge the delta
    # for any mid-period immediate change. Using the CURRENT sub.plan_version_id
    # (which an immediate change already advanced to the NEW plan) billed the new
    # plan at full price for the whole period AND added the upgrade proration —
    # double-charging the delta. The period-start plan is the `from_*` of the
    # first immediate change inside this period; if none, the sub hasn't changed
    # since the period opened, so its current plan/seats ARE the period-start
    # values.
    first_change = (
        await db.execute(
            select(SubscriptionChange)
            .where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.proration_mode == "immediate",
                SubscriptionChange.change_type.in_(["plan_change", "seat_change"]),
                SubscriptionChange.effective_at >= period.period_start,
                SubscriptionChange.effective_at < period.period_end,
            )
            .order_by(SubscriptionChange.effective_at, SubscriptionChange.id)
            .limit(1)
        )
    ).scalar_one_or_none()
    start_version_id = first_change.from_plan_version_id if first_change else sub.plan_version_id
    start_seats = (
        first_change.from_seats
        if first_change and first_change.from_seats is not None
        else sub.seat_quantity
    )
    version = await db.get(PlanVersion, start_version_id)
    plan = await db.get(ProductPlan, version.plan_id)
    price = (
        await db.execute(
            select(PlanPrice).where(
                PlanPrice.plan_version_id == version.id,
                PlanPrice.currency == sub.currency,
                PlanPrice.interval == sub.interval,
            )
        )
    ).scalar_one_or_none()

    # Blocked ratings abort the invoice for this cycle (RATING_INCOMPLETE)
    blocked = (
        await db.execute(
            select(func.count(RatedUsage.id)).where(
                RatedUsage.tenant_id == tenant.id, RatedUsage.status == "blocked"
            )
        )
    ).scalar_one()
    if blocked:
        # reopen the period — retried next close cycle after ops fix FX
        await db.execute(
            update(BillingPeriod)
            .where(BillingPeriod.id == period_id)
            .values(status="open", closed_at=None)
        )
        log.warning("cp_invoice_blocked_ratings", tenant_id=tenant.id, blocked=blocked)
        return None

    invoice = Invoice(
        tenant_id=tenant.id,
        billing_period_id=period.id,
        currency=sub.currency,
        provider=sub.provider,
        issued_at=_now(),
        due_at=_now() + timedelta(days=14),
    )
    db.add(invoice)
    await db.flush()
    lines: list[InvoiceLine] = []
    sort = 0

    # a. plan line(s) — per change-log segments (single line when unchanged)
    plan_amount = price.amount_minor if price else 0
    lines.append(
        InvoiceLine(
            invoice_id=invoice.id,
            line_type="plan",
            description=(
                f"{plan.name} plan — "
                f"{period.period_start.date().isoformat()} to {period.period_end.date().isoformat()}"
            ),
            quantity=1,
            unit_amount_minor=plan_amount,
            amount_minor=plan_amount,
            sort_order=sort,
        )
    )
    sort += 1

    # b. seats line: max(actual peak, reserved floor) minus included
    from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole

    live_seats = (
        await db.execute(
            select(func.count(func.distinct(OrgMember.user_id)))
            .select_from(OrgMember)
            .join(Organization, Organization.id == OrgMember.org_id)
            .where(
                Organization.tenant_id == tenant.id,
                OrgMember.status == MemberStatus.ACTIVE,
                OrgMember.role == OrgRole.STUDENT,
            )
        )
    ).scalar_one()
    # Use the PERIOD-START reserved floor, not the post-change sub.seat_quantity:
    # a mid-period immediate seat increase is billed by the proration line below,
    # so counting the raised floor here too double-charged the delta (R41[2]).
    billable_seats = max(live_seats, start_seats)
    included = price.included_seats if price else 0
    overage_seats = max(billable_seats - included, 0)
    seat_price = (price.overage_seat_amount_minor or 0) if price else 0
    if overage_seats and seat_price:
        lines.append(
            InvoiceLine(
                invoice_id=invoice.id,
                line_type="seats",
                description=f"{overage_seats} seats over included {included}",
                quantity=overage_seats,
                unit_amount_minor=seat_price,
                amount_minor=overage_seats * seat_price,
                sort_order=sort,
            )
        )
        sort += 1

    # c. usage lines: un-invoiced rated usage grouped by type
    from app.controlplane.models.usage import UsageEvent

    usage_rows = (
        await db.execute(
            select(
                RatedUsage.usage_type,
                # R75: bill the SUM of exact per-event amounts, rounded ONCE
                # here (round-of-sum). Summing the per-event rounded integers
                # (billable_amount_minor) drops every event whose marginal
                # charge was < 0.5 minor to 0 — unbounded under-billing.
                func.sum(RatedUsage.billable_amount_exact).label("amount_exact"),
                func.sum(RatedUsage.quantity).label("qty"),
                func.count(RatedUsage.id).label("events"),
            )
            .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
            .where(
                RatedUsage.tenant_id == tenant.id,
                RatedUsage.status == "rated",
                RatedUsage.billable_currency == sub.currency,
                # In-period CONSUMPTION bills here even if rated late; usage
                # occurring after period end waits for the next invoice.
                UsageEvent.occurred_at < period.period_end,
            )
            .group_by(RatedUsage.usage_type)
        )
    ).all()
    for row in usage_rows:
        amount = int(Decimal(row.amount_exact or 0).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if amount == 0:
            continue
        line = InvoiceLine(
            invoice_id=invoice.id,
            line_type="usage",
            description=f"Usage: {row.usage_type.replace('_', ' ')}",
            quantity=row.qty,
            amount_minor=amount,
            usage_summary={
                "usage_type": row.usage_type,
                "event_count": int(row.events),
                "total_quantity": str(row.qty),
                "period_start": period.period_start.isoformat(),
                "period_end": period.period_end.isoformat(),
            },
            sort_order=sort,
        )
        lines.append(line)
        sort += 1
    for line in lines:
        db.add(line)
    await db.flush()
    # Bind rated rows to their usage lines
    for line in lines:
        if line.line_type != "usage":
            continue
        in_period_event_ids = select(UsageEvent.id).where(
            UsageEvent.occurred_at < period.period_end
        )
        await db.execute(
            update(RatedUsage)
            .where(
                RatedUsage.tenant_id == tenant.id,
                RatedUsage.status == "rated",
                RatedUsage.usage_type == line.usage_summary["usage_type"],
                RatedUsage.billable_currency == sub.currency,
                RatedUsage.usage_event_id.in_(in_period_event_ids),
            )
            .values(status="invoiced", invoice_line_id=line.id)
        )

    # d. license lines (bill_via_invoice purchases — P8 wires the flag)
    try:
        from app.controlplane.models.marketplace import MarketplacePurchase

        pending_licenses = (
            (
                await db.execute(
                    select(MarketplacePurchase).where(
                        MarketplacePurchase.buyer_tenant_id == tenant.id,
                        MarketplacePurchase.status == "paid",
                        MarketplacePurchase.invoice_id.is_(None),
                        MarketplacePurchase.payment_method == "invoice",
                    )
                )
            )
            .scalars()
            .all()
        )
        for purchase in pending_licenses:
            db.add(
                InvoiceLine(
                    invoice_id=invoice.id,
                    line_type="license",
                    description=f"Content license {purchase.listing_id}",
                    quantity=1,
                    amount_minor=purchase.amount_minor,
                    sort_order=sort,
                )
            )
            purchase.invoice_id = invoice.id
            sort += 1
    except ImportError:
        pass  # marketplace lands in P8

    # e. proration lines from uninvoiced change-log segments
    changes = (
        (
            await db.execute(
                select(SubscriptionChange).where(
                    SubscriptionChange.subscription_id == sub.id,
                    SubscriptionChange.invoiced.is_(False),
                    SubscriptionChange.proration_mode == "immediate",
                    SubscriptionChange.effective_at < period.period_end,
                    SubscriptionChange.change_type.in_(["plan_change", "seat_change"]),
                )
            )
        )
        .scalars()
        .all()
    )
    for change in changes:
        old_p = (
            await db.execute(
                select(PlanPrice).where(
                    PlanPrice.plan_version_id == change.from_plan_version_id,
                    PlanPrice.currency == sub.currency,
                    PlanPrice.interval == sub.interval,
                )
            )
        ).scalar_one_or_none()
        new_p = (
            await db.execute(
                select(PlanPrice).where(
                    PlanPrice.plan_version_id == change.to_plan_version_id,
                    PlanPrice.currency == sub.currency,
                    PlanPrice.interval == sub.interval,
                )
            )
        ).scalar_one_or_none()
        preview = proration_preview(
            period_start=period.period_start,
            period_end=period.period_end,
            at=change.effective_at,
            old_amount_minor=old_p.amount_minor if old_p else 0,
            new_amount_minor=new_p.amount_minor if new_p else 0,
            old_seats=change.from_seats or 0,
            new_seats=change.to_seats or 0,
            seat_price_minor=(new_p.overage_seat_amount_minor or 0) if new_p else 0,
        )
        if preview["net_minor"] != 0:
            db.add(
                InvoiceLine(
                    invoice_id=invoice.id,
                    line_type="proration",
                    description=(
                        f"Plan change on {change.effective_at.date().isoformat()} "
                        f"({preview['days_left']} days remaining)"
                    ),
                    quantity=1,
                    amount_minor=preview["net_minor"],
                    sort_order=sort,
                )
            )
            sort += 1
        change.invoiced = True

    # f+g. totals + credit application
    await db.flush()
    subtotal = (
        await db.execute(
            select(func.coalesce(func.sum(InvoiceLine.amount_minor), 0)).where(
                InvoiceLine.invoice_id == invoice.id
            )
        )
    ).scalar_one()
    invoice.subtotal_minor = subtotal
    # R75[14]: a net-negative subtotal (e.g. a large immediate-downgrade credit
    # exceeding the period's charges) is money OWED to the tenant, not zero.
    # Clamping total to 0 silently discarded it — the change rows are already
    # flagged invoiced, so it was never carried forward or refunded. Instead,
    # refund the residual to the credit ledger as a carry-forward and bill 0.
    total = max(subtotal, 0)
    if subtotal < 0:
        await credit_svc.refund(
            db,
            tenant.id,
            sub.currency,
            -subtotal,
            reference_type="invoice",
            reference_id=invoice.id,
            reason="Negative invoice balance carried forward as credit",
            actor=SYSTEM_ACTOR,
            idempotency_key=f"invneg:{invoice.id}",
        )
    from app.controlplane.models.credit import TenantCreditBalance

    # Lock the balance row while we read available credit and decide how much to
    # apply, and hold it through the debit below. A previous UNLOCKED read here
    # computed credit_to_apply from a stale copy: a concurrent top-up/debit
    # between this read and the debit could make us under-apply credit (tenant
    # over-billed) or trip the debit's INSUFFICIENT_CREDIT check and abort the
    # whole close. FOR UPDATE + populate_existing serializes credit application
    # against concurrent balance mutations; the debit below re-locks the same
    # row reentrantly within this transaction.
    balance = (
        await db.execute(
            select(TenantCreditBalance)
            .where(
                TenantCreditBalance.tenant_id == tenant.id,
                TenantCreditBalance.currency == sub.currency,
            )
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
    credit_available = (balance.balance_minor - balance.reserved_minor) if balance else 0
    credit_to_apply = min(credit_available, total)
    if credit_to_apply > 0:
        await credit_svc.debit(
            db,
            tenant.id,
            sub.currency,
            credit_to_apply,
            reference_type="invoice",
            reference_id=invoice.id,
            idempotency_key=f"invcredit:{invoice.id}",
        )
        db.add(
            InvoiceLine(
                invoice_id=invoice.id,
                line_type="credit",
                description="Credit balance applied",
                quantity=1,
                amount_minor=-credit_to_apply,
                sort_order=sort,
            )
        )
        invoice.credit_applied_minor = credit_to_apply
    invoice.total_minor = total
    invoice.amount_due_minor = total - credit_to_apply

    await finalize_invoice(db, invoice, actor=SYSTEM_ACTOR)

    # Roll the subscription into the next period (or cancel at period end)
    if sub.status == "cancel_at_period_end":
        await db.execute(
            update(Subscription)
            .where(Subscription.id == sub.id, Subscription.status == "cancel_at_period_end")
            .values(status="cancelled", cancelled_at=_now())
        )
        await invalidate_cache(tenant.id)
    elif sub.status == "cancelled":
        # R41[4]: this is the final partial-period invoice for an immediately
        # cancelled subscription — bill it, but do NOT open a new period.
        pass
    else:
        # R41[0]: APPLY any scheduled next_period changes now. change_plan
        # records a next_period change (effective_at = period_end) but only
        # mutates the subscription for immediate changes — nothing ever applied
        # the deferred plan/seat change, so a downgrade never took effect and the
        # tenant was billed the old (higher) plan every subsequent period. At
        # rollover, walk the pending next_period changes due by this period_end
        # in order and fold them into the subscription, then mark them invoiced
        # (they carry no proration line — the switch simply takes effect for the
        # upcoming period, billed in arrears next close).
        pending = (
            (
                await db.execute(
                    select(SubscriptionChange)
                    .where(
                        SubscriptionChange.subscription_id == sub.id,
                        SubscriptionChange.invoiced.is_(False),
                        SubscriptionChange.proration_mode == "next_period",
                        SubscriptionChange.change_type.in_(["plan_change", "seat_change"]),
                        SubscriptionChange.effective_at <= period.period_end,
                    )
                    .order_by(SubscriptionChange.effective_at, SubscriptionChange.id)
                )
            )
            .scalars()
            .all()
        )
        for change in pending:
            if change.to_plan_version_id is not None:
                sub.plan_version_id = change.to_plan_version_id
            if change.to_seats is not None:
                sub.seat_quantity = change.to_seats
            change.invoiced = True
        if pending:
            await invalidate_cache(tenant.id)
            # R64[16]: push the now-applied deferred change to the provider so
            # its recurring billing follows the new plan/quantity. Best-effort:
            # a provider hiccup must not abort the period close (the outbox
            # retry would double-generate); ops sees the error log.
            if sub.provider in ("mock", "stripe") and sub.external_ref:
                from app.controlplane.services.billing_providers import get_billing_provider

                adapter = get_billing_provider(sub.provider)
                new_p = (
                    await db.execute(
                        select(PlanPrice).where(
                            PlanPrice.plan_version_id == sub.plan_version_id,
                            PlanPrice.currency == sub.currency,
                            PlanPrice.interval == sub.interval,
                        )
                    )
                ).scalar_one_or_none()
                if adapter is not None and new_p is not None:
                    try:
                        await adapter.change_subscription(
                            sub.external_ref,
                            new_p.external_price_ref or "",
                            sub.seat_quantity,
                        )
                    except Exception:  # noqa: BLE001
                        log.error(
                            "cp_provider_change_push_failed",
                            subscription_id=sub.id,
                            provider=sub.provider,
                        )

        next_start = period.period_end
        next_end = _add_interval(next_start, sub.interval)
        sub.current_period_start = next_start
        sub.current_period_end = next_end
        db.add(
            BillingPeriod(
                tenant_id=tenant.id,
                subscription_id=sub.id,
                period_start=next_start,
                period_end=next_end,
            )
        )
    await db.execute(
        update(BillingPeriod).where(BillingPeriod.id == period_id).values(status="invoiced")
    )
    await db.flush()
    return invoice


async def finalize_invoice(db: AsyncSession, invoice: Invoice, *, actor: Actor) -> Invoice:
    """draft → open + number assignment. Concurrency-safe: sequence FOR UPDATE
    + guarded transition; a lost race rolls the sequence back with the tx."""
    number = await _next_invoice_number(db)
    result = await db.execute(
        update(Invoice)
        .where(Invoice.id == invoice.id, Invoice.status == "draft")
        .values(status="open", number=number, finalized_at=_now())
    )
    if not result.rowcount:
        raise AppError("INVOICE_NOT_DRAFT", "Invoice already finalized", 409)
    await db.refresh(invoice)
    if invoice.amount_due_minor == 0:
        await db.execute(
            update(Invoice)
            .where(Invoice.id == invoice.id, Invoice.status == "open")
            .values(status="paid", paid_at=_now())
        )
        await db.refresh(invoice)
    await record_audit(
        db,
        actor=actor,
        action="invoice.finalized",
        target_type="invoice",
        target_id=invoice.id,
        tenant_id=invoice.tenant_id,
        after={"number": invoice.number, "total_minor": invoice.total_minor},
    )
    enqueue(db, "invoice.finalized", {"invoice_id": invoice.id})
    return invoice


def require_mutable(invoice: Invoice) -> None:
    """Post-finalize edits are rejected — corrections via CreditNote only."""
    if invoice.status != "draft":
        raise AppError("INVOICE_FINALIZED", "Finalized invoices are immutable", 409)


async def record_payment(
    db: AsyncSession,
    invoice: Invoice,
    *,
    amount_minor: int,
    method: str,
    external_ref: str | None,
    reference_note: str | None,
    received_at: datetime | None,
    actor: Actor,
) -> PaymentRecord:
    if invoice.status not in ("open", "paid"):
        raise AppError("INVOICE_NOT_OPEN", "Invoice is not open for payment", 409)
    payment = PaymentRecord(
        invoice_id=invoice.id,
        tenant_id=invoice.tenant_id,
        amount_minor=amount_minor,
        currency=invoice.currency,
        method=method,
        status="succeeded",
        external_ref=external_ref,
        reference_note=reference_note,
        received_at=received_at or _now(),
        recorded_by=actor.user_id,
    )
    db.add(payment)
    await db.flush()
    paid_total = (
        await db.execute(
            select(func.coalesce(func.sum(PaymentRecord.amount_minor), 0)).where(
                PaymentRecord.invoice_id == invoice.id,
                PaymentRecord.status == "succeeded",
            )
        )
    ).scalar_one()
    if paid_total >= invoice.amount_due_minor and invoice.status == "open":
        await db.execute(
            update(Invoice)
            .where(Invoice.id == invoice.id, Invoice.status == "open")
            .values(status="paid", paid_at=_now())
        )
        tenant = await db.get(TenantAccount, invoice.tenant_id)
        if tenant is not None and tenant.status == TenantStatus.PAST_DUE:
            from app.controlplane.services.tenants import transition_status

            await transition_status(db, tenant, TenantStatus.ACTIVE, actor=SYSTEM_ACTOR)
    await record_audit(
        db,
        actor=actor,
        action="invoice.payment_recorded",
        target_type="invoice",
        target_id=invoice.id,
        tenant_id=invoice.tenant_id,
        after={"amount_minor": amount_minor, "method": method},
    )
    return payment


async def void_invoice(db: AsyncSession, invoice: Invoice, *, reason: str, actor: Actor) -> Invoice:
    if invoice.status == "paid":
        raise AppError("INVOICE_NOT_OPEN", "Paid invoices need a credit note, not a void", 409)
    result = await db.execute(
        update(Invoice)
        .where(Invoice.id == invoice.id, Invoice.status.in_(["draft", "open"]))
        .values(status="void", voided_at=_now(), void_reason=reason)
    )
    if not result.rowcount:
        raise AppError("INVOICE_NOT_OPEN", "Invoice state changed concurrently", 409)
    # Unbind rated rows so they can be re-invoiced next cycle
    line_ids = (
        (
            await db.execute(
                select(InvoiceLine.id).where(
                    InvoiceLine.invoice_id == invoice.id, InvoiceLine.line_type == "usage"
                )
            )
        )
        .scalars()
        .all()
    )
    if line_ids:
        await db.execute(
            update(RatedUsage)
            .where(RatedUsage.invoice_line_id.in_(line_ids))
            .values(status="rated", invoice_line_id=None)
        )
    # R56[24]: reverse any revenue-share accrual sourced from this invoice —
    # the re-invoice will accrue afresh at its own finalize, so leaving the
    # original entry standing double-paid the partner.
    from app.controlplane.services.revenue_share import reverse_invoice_accruals

    await reverse_invoice_accruals(db, invoice.id)

    # R41[3]: a period invoice consumed its period's SubscriptionChange proration
    # (flipped change.invoiced=True) and rolled the period to 'invoiced'. Voiding
    # it only unbound usage rows — the plan fee, seat charges and proration were
    # silently dropped and the change.invoiced flag stayed set, so the next close
    # never re-billed them. Recover by rewinding the close: reopen this period,
    # delete the forward period the close created, roll the subscription back to
    # this period's window, and un-invoice its changes — so the next close cycle
    # regenerates the full invoice and re-rolls cleanly. (Manual invoices have no
    # billing_period_id — nothing to rewind.)
    if invoice.billing_period_id is not None:
        period = await db.get(BillingPeriod, invoice.billing_period_id)
        if period is not None:
            sub = await db.get(Subscription, period.subscription_id)
            await db.execute(
                update(BillingPeriod)
                .where(BillingPeriod.id == period.id)
                .values(status="open", closed_at=None)
            )
            if sub is not None:
                # Delete the period the original close rolled forward to (any
                # period of this sub starting at/after this period's end) so the
                # re-close doesn't collide on uq_cp_period.
                await db.execute(
                    delete(BillingPeriod).where(
                        BillingPeriod.subscription_id == sub.id,
                        BillingPeriod.period_start >= period.period_end,
                    )
                )
                # Un-invoice this period's immediate changes AND any next_period
                # change the close applied at this period's rollover (effective_at
                # == period_end), then roll the subscription window back so the
                # arrears re-close bills this period again.
                await db.execute(
                    update(SubscriptionChange)
                    .where(
                        SubscriptionChange.subscription_id == sub.id,
                        SubscriptionChange.invoiced.is_(True),
                        SubscriptionChange.effective_at >= period.period_start,
                        SubscriptionChange.effective_at <= period.period_end,
                    )
                    .values(invoiced=False)
                )
                sub.current_period_start = period.period_start
                sub.current_period_end = period.period_end
                # A sub cancelled by this period's close must go back to active so
                # the re-close can run and roll it forward again.
                if sub.status == "cancelled":
                    sub.status = "active"
                    sub.cancelled_at = None
                await invalidate_cache(sub.tenant_id)
    await record_audit(
        db,
        actor=actor,
        action="invoice.voided",
        target_type="invoice",
        target_id=invoice.id,
        tenant_id=invoice.tenant_id,
        reason=reason,
    )
    await db.refresh(invoice)
    return invoice


async def issue_credit_note(
    db: AsyncSession, invoice: Invoice, *, amount_minor: int, reason: str, actor: Actor
) -> CreditNote:
    """The ONLY correction path for finalized invoices: an explicit credit
    note that lands as a credit-ledger refund for the next cycle."""
    if invoice.status not in ("open", "paid"):
        raise AppError("INVOICE_NOT_OPEN", "Credit notes apply to finalized invoices", 409)
    if amount_minor <= 0 or amount_minor > invoice.total_minor:
        raise AppError("PAYMENT_INVALID", "Credit note exceeds invoice total", 422)
    note = CreditNote(
        invoice_id=invoice.id,
        tenant_id=invoice.tenant_id,
        amount_minor=amount_minor,
        currency=invoice.currency,
        reason=reason,
        status="applied",
        created_by=actor.user_id,
    )
    db.add(note)
    await db.flush()
    await credit_svc.refund(
        db,
        invoice.tenant_id,
        invoice.currency,
        amount_minor,
        reference_type="credit_note",
        reference_id=note.id,
        reason=reason,
        actor=actor,
        idempotency_key=f"cn:{note.id}",
    )
    await record_audit(
        db,
        actor=actor,
        action="invoice.credit_note_issued",
        target_type="invoice",
        target_id=invoice.id,
        tenant_id=invoice.tenant_id,
        after={"credit_note_id": note.id, "amount_minor": amount_minor},
        reason=reason,
    )
    enqueue(db, "credit_note.applied", {"credit_note_id": note.id, "invoice_id": invoice.id})
    return note


# ── Period-close scan + outbox handler ───────────────────────


async def scan_due_periods(db: AsyncSession) -> int:
    """Hourly cron: enqueue period.close_due for every due subscription."""
    due = (
        (
            await db.execute(
                select(BillingPeriod.id)
                .join(Subscription, Subscription.id == BillingPeriod.subscription_id)
                .where(
                    BillingPeriod.status == "open",
                    BillingPeriod.period_end <= _now(),
                    Subscription.status.in_(["active", "cancel_at_period_end", "past_due"]),
                )
            )
        )
        .scalars()
        .all()
    )
    for period_id in due:
        enqueue(db, "period.close_due", {"billing_period_id": period_id})
    return len(due)


@register_handler("period.close_due")
async def _handle_period_close(db: AsyncSession, payload: dict) -> None:
    await close_period_and_invoice(db, payload["billing_period_id"])


# ── Webhook processing (ADR-014 §6.5) ────────────────────────


async def process_webhook(
    db: AsyncSession, provider_key: str, headers: dict, raw_body: bytes
) -> dict:
    from app.controlplane.services.billing_providers import get_billing_provider

    adapter = get_billing_provider(provider_key)
    if adapter is None or provider_key == "manual":
        raise AppError("WEBHOOK_SIGNATURE_INVALID", "Unknown billing provider", 401)
    parsed = adapter.verify_webhook(headers, raw_body)  # raises 401 pre-storage

    from sqlalchemy.dialects.postgresql import insert as pg_insert
    from ulid import ULID

    stmt = (
        pg_insert(BillingWebhookEvent)
        .values(
            id=str(ULID()),
            provider=provider_key,
            external_event_id=parsed.external_event_id,
            event_type=parsed.event_type,
            payload=parsed.data,
        )
        .on_conflict_do_nothing(index_elements=["provider", "external_event_id"])
        .returning(BillingWebhookEvent.id)
    )
    event_id = (await db.execute(stmt)).scalar_one_or_none()
    if event_id is None:
        return {"duplicate": True}  # replay — single-effect guarantee
    event = await db.get(BillingWebhookEvent, event_id)
    try:
        handled = await _apply_webhook_event(db, provider_key, parsed)
        event.status = "processed" if handled else "ignored"
        event.processed_at = _now()
    except Exception as exc:  # noqa: BLE001 — recorded for manual replay
        event.status = "failed"
        event.error = str(exc)[:2000]
        log.error("cp_webhook_failed", provider=provider_key, event_type=parsed.event_type)
    await db.flush()
    return {"duplicate": False, "status": event.status}


def _subscription_ref(data: dict) -> str | None:
    """The subscription id from a Stripe payload, tolerant of API versions.

    R64[19]: Stripe API 2025-03+ ("basil") moved Invoice.subscription to
    parent.subscription_details.subscription; checkout sessions keep the
    top-level field. Read both shapes so dunning transitions don't go dead
    against a new-API webhook endpoint."""
    ref = data.get("subscription")
    if ref:
        return ref if isinstance(ref, str) else ref.get("id")
    parent = data.get("parent") or {}
    details = parent.get("subscription_details") or {}
    ref = details.get("subscription")
    if ref:
        return ref if isinstance(ref, str) else ref.get("id")
    return None


async def _apply_webhook_event(db: AsyncSession, provider: str, parsed) -> bool:
    """Event map (§6.2). Tenant status changes go through the guarded
    transition table — provider state is never blindly trusted."""
    data = parsed.data
    event_type = parsed.event_type
    meta = data.get("metadata") or {}
    tenant_id = meta.get("tenant_id")

    if event_type in (
        "checkout.session.completed",
        "checkout.completed",
        # R64[15]: delayed-notification payment methods settle later — Stripe
        # signals the outcome with these; deliver on success, ignore failure
        # (money never arrived, nothing was delivered).
        "checkout.session.async_payment_succeeded",
    ):
        if tenant_id is None:
            return False
        tenant = await db.get(TenantAccount, tenant_id)
        if tenant is None:
            return False
        # R64[15]: Stripe fires checkout.session.completed the moment the
        # checkout UI finishes, even with payment_status='unpaid' for
        # delayed-notification methods (SEPA/ACH/boleto/OXXO). Delivering the
        # goods (license, credits, subscription) before money settles is a free
        # ride when the payment later fails. Only proceed for paid/no-cost
        # sessions; an async-payment session completes via
        # checkout.session.async_payment_succeeded (handled below). Events
        # without the field (mock provider) keep the old behavior.
        payment_status = data.get("payment_status")
        if payment_status is not None and payment_status not in ("paid", "no_payment_required"):
            log.info(
                "cp_checkout_awaiting_async_payment",
                session=data.get("id"),
                payment_status=payment_status,
            )
            return True  # recorded; async_payment_succeeded will deliver
        kind = meta.get("kind", "subscription")
        if kind == "subscription":
            await activate_subscription_from_checkout(
                db,
                tenant,
                plan_key=meta.get("plan_key", "school"),
                interval=meta.get("interval", "month"),
                seats=int(meta.get("seats", "0") or 0),
                provider=provider,
                external_customer_ref=data.get("customer"),
                external_ref=_subscription_ref(data) or data.get("id"),
            )
        elif kind == "credit_topup":
            await credit_svc.top_up(
                db,
                tenant.id,
                tenant.currency,
                int(data.get("amount_total") or meta.get("amount_minor") or 0),
                reference_type="checkout",
                reference_id=str(data.get("id")),
                idempotency_key=f"checkout:{data.get('id')}",
                actor=SYSTEM_ACTOR,
            )
        elif kind == "purchase":
            try:
                from app.controlplane.services.marketplace import mark_purchase_paid

                await mark_purchase_paid(
                    db,
                    purchase_id=meta.get("purchase_id"),
                    payment_ref=str(data.get("id")),
                    actor=SYSTEM_ACTOR,
                )
            except ImportError:
                return False
        return True

    if event_type in ("invoice.paid", "payment.succeeded"):
        sub = (
            await db.execute(
                select(Subscription).where(
                    Subscription.external_ref == (_subscription_ref(data) or ""),
                    Subscription.status != "cancelled",
                )
            )
        ).scalar_one_or_none()
        if sub is None:
            return False
        # The subscription itself must leave past_due too — reactivating only
        # the tenant left the sub permanently stuck (R42[6]).
        await db.execute(
            update(Subscription)
            .where(Subscription.id == sub.id, Subscription.status == "past_due")
            .values(status="active")
        )
        tenant = await db.get(TenantAccount, sub.tenant_id)
        if tenant is not None and tenant.status == TenantStatus.PAST_DUE:
            from app.controlplane.services.tenants import transition_status

            await transition_status(db, tenant, TenantStatus.ACTIVE, actor=SYSTEM_ACTOR)
        return True

    if event_type in ("invoice.payment_failed", "payment.failed"):
        sub = (
            await db.execute(
                select(Subscription).where(
                    Subscription.external_ref == (_subscription_ref(data) or ""),
                    Subscription.status != "cancelled",
                )
            )
        ).scalar_one_or_none()
        if sub is None:
            return False
        tenant = await db.get(TenantAccount, sub.tenant_id)
        if tenant is not None and tenant.status == TenantStatus.ACTIVE:
            from app.controlplane.services.tenants import transition_status

            await transition_status(
                db, tenant, TenantStatus.PAST_DUE, actor=SYSTEM_ACTOR, reason="payment failed"
            )
            await db.execute(
                update(Subscription)
                .where(Subscription.id == sub.id, Subscription.status == "active")
                .values(status="past_due")
            )
        return True

    if event_type == "customer.subscription.deleted":
        sub = (
            await db.execute(
                select(Subscription).where(
                    Subscription.external_ref == (data.get("id") or ""),
                    Subscription.status != "cancelled",
                )
            )
        ).scalar_one_or_none()
        if sub is None:
            return False
        await db.execute(
            update(Subscription)
            .where(Subscription.id == sub.id, Subscription.status != "cancelled")
            .values(status="cancelled", cancelled_at=_now())
        )
        await invalidate_cache(sub.tenant_id)
        return True

    return False  # unknown event type → ignored (200, no retry storm)
