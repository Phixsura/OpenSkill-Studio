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
        await record_audit(
            db,
            actor=actor,
            action="subscription.started",
            target_type="subscription",
            target_id=sub.id,
            tenant_id=tenant.id,
            after={"plan_key": plan_key, "interval": interval, "provider": provider},
        )
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
        metadata={
            "plan_key": plan_key,
            "interval": interval,
            "seats": str(seats),
            # R80[2]: pin the version the CUSTOMER SAW at checkout. The
            # completion webhook can land minutes-to-days later (async
            # payment methods); re-resolving "current active" then races
            # plan-version activation and binds the paid customer to a
            # version/price they never agreed to.
            "plan_version_id": version.id,
        },
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
    pinned_version_id: str | None = None,
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
    version = None
    if pinned_version_id:
        # R80[2]: bind to the version pinned at checkout time (what the
        # customer actually saw and paid for), even if ops activated a newer
        # version while the payment settled. Fall back to re-resolution only
        # when the pin is absent (legacy sessions) or dangling.
        version = await db.get(PlanVersion, pinned_version_id)
        if version is not None and version.status == "draft":
            version = None  # a draft was never purchasable — resolve fresh
    if version is None:
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
    elif tenant.status == TenantStatus.SUSPENDED and tenant.suspension_reason == "trial expired":
        # R54[2]: with trial_expiry_action='suspend', the hourly cron could
        # suspend a still-TRIAL tenant DURING their checkout — the webhook
        # then only handled TRIAL, stranding a PAYING customer in suspension
        # (provider billing live, platform dark). Rescue exactly the cron's
        # suspension; admin suspensions (abuse) are never self-serviceable
        # by payment, hence the reason match.
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
    # R97[m12]: lock the sub row and refresh — the caller's copy may be stale
    # (concurrent immediate change / period close, which both lock this row).
    # Two unserialized changes recorded stale from_seats/from_plan in their
    # SubscriptionChange rows, corrupting the proration basis at close.
    sub = (
        await db.execute(
            select(Subscription)
            .where(Subscription.id == sub.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
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
    # R60[40]: capture the PRE-change seat count before the immediate branch
    # mutates sub.seat_quantity — the audit 'before' payload read the mutated
    # value, so before.seats always equaled after.seats.
    old_seats = sub.seat_quantity
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
        # R101[M39]: pushed via the outbox — the old inline HTTP call ran
        # while holding the m12 FOR UPDATE on the subscription row, blocking
        # every concurrent close/cancel for the tenant for up to the provider
        # timeout. The missing-ref 409 pre-check stays inline for immediate
        # user feedback.
        if sub.provider in ("mock", "stripe") and sub.external_ref:
            if (
                sub.provider == "stripe"
                and new_price is not None
                and not new_price.external_price_ref
            ):
                raise AppError(
                    "PLAN_NOT_AVAILABLE",
                    "Target plan price has no Stripe price configured",
                    409,
                )
            enqueue(db, "subscription.push_provider", {"subscription_id": sub.id})
    await db.flush()
    await record_audit(
        db,
        actor=actor,
        action="subscription.plan_changed",
        target_type="subscription",
        target_id=sub.id,
        tenant_id=tenant.id,
        before={"plan_version_id": old_version.id, "seats": old_seats},
        after={"plan_version_id": new_version.id, "seats": new_seats, "mode": mode},
    )
    await invalidate_cache(tenant.id)
    return {"proration": preview, "mode": mode}


async def reactivate_subscription(
    db: AsyncSession,
    tenant: TenantAccount,
    sub: Subscription,
    *,
    actor: Actor,
) -> Subscription:
    """R82[M0]: cancel_at_period_end was IRREVERSIBLE — nothing cleared the
    flag, start_subscription 409'd on the live-sub partial index, and the
    customer who changed their mind had to wait out the period and re-onboard.
    Guarded un-cancel; the provider-side flag is cleared too."""
    result = await db.execute(
        update(Subscription)
        .where(Subscription.id == sub.id, Subscription.status == "cancel_at_period_end")
        .values(status="active", cancel_at_period_end=False)
    )
    if not result.rowcount:
        raise AppError(
            "SUBSCRIPTION_STATUS_CONFLICT",
            "Only a pending-cancellation subscription can be reactivated",
            409,
        )
    db.add(
        SubscriptionChange(
            subscription_id=sub.id,
            change_type="reactivate",
            effective_at=_now(),
            proration_mode="immediate",
            created_by=actor.user_id,
        )
    )
    if sub.provider in ("mock", "stripe") and sub.external_ref:
        # R101[H17]: always via the outbox push handler — it resolves the real
        # price ref (the old inline call passed "" which Stripe rejects) and
        # change_subscription now clears provider-side cancel_at_period_end,
        # so the un-cancel actually sticks on the provider. Retries + visible
        # dead-letter come free.
        enqueue(db, "subscription.push_provider", {"subscription_id": sub.id})
    await record_audit(
        db,
        actor=actor,
        action="subscription.reactivated",
        target_type="subscription",
        target_id=sub.id,
        tenant_id=tenant.id,
    )
    await invalidate_cache(tenant.id)
    await db.refresh(sub)
    return sub


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
        # R113[M20/M34]: via the outbox — the old inline provider call ran
        # under the guarded-UPDATE state transition (and the row lock), so a
        # provider timeout/5xx rolled back the WHOLE cancel: the customer was
        # told "cancelled" while nothing happened platform-side, or worse the
        # provider cancel succeeded and the platform commit then failed,
        # leaving the provider dark while we kept the sub live. Enqueue is
        # atomic with the state change; the handler retries with backoff and
        # dead-letters visibly. Refs are pinned at cancel time so a stale
        # retry can never cancel a later re-subscription's new provider sub.
        enqueue(
            db,
            "subscription.cancel_provider",
            {
                "subscription_id": sub.id,
                "at_period_end": at_period_end,
                "external_ref": sub.external_ref,
                "provider": sub.provider,
            },
        )
    await record_audit(
        db,
        actor=actor,
        action="subscription.cancelled",
        target_type="subscription",
        target_id=sub.id,
        tenant_id=tenant.id,
        after={"at_period_end": at_period_end},
    )
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
    # R80[4]: LOCK the subscription for the whole close. The terminal branch
    # at the end reads sub.status — an unlocked read is stale against a
    # concurrent cancel(at_period_end) landing mid-close: the close rolled
    # the freshly-cancelled sub into a NEW open period (an extra full period
    # billed), or conversely finalized totals off a plan a concurrent
    # immediate-change just swapped. FOR UPDATE + populate_existing makes
    # cancel/change (guarded UPDATEs on this row) wait until the close
    # commits, and the close itself sees the latest committed state.
    sub = (
        await db.execute(
            select(Subscription)
            .where(Subscription.id == period.subscription_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one_or_none()
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
                # R81/R82[1]: NO upper bound. The hourly close runs up to ~1h
                # after period_end; an immediate change landing in that gap
                # already mutated sub.plan_version_id/seat_quantity, so the
                # fallback below would bill the ENTIRE just-ended period at
                # the NEW plan/seats. The earliest immediate change since
                # period_start — wherever it lands — carries the true
                # period-start values in its from_*. (Gap changes are
                # prorated in the NEXT period, whose window they fall into;
                # this period must simply bill the old plan unprorated.)
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
    # R82[2]: an immediate cancel truncates period_end to now — the flat
    # amount then charged the FULL interval fee for a partial period (cancel
    # on day 2 of a monthly plan billed all 30 days). Prorate by the actual
    # period length over the natural interval length. Untruncated periods
    # compute a ratio of exactly 1 (period_end == natural end), so the
    # normal path is numerically unchanged.
    natural_end = _add_interval(period.period_start, sub.interval)
    natural_seconds = (natural_end - period.period_start).total_seconds()
    actual_seconds = (period.period_end - period.period_start).total_seconds()
    if natural_seconds > 0 and actual_seconds < natural_seconds:
        ratio = max(Decimal(actual_seconds), Decimal(0)) / Decimal(natural_seconds)
        plan_amount = int(
            (Decimal(plan_amount) * ratio).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
        )
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
    from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus

    live_seats = (
        await db.execute(
            select(func.count(func.distinct(OrgMember.user_id)))
            .select_from(OrgMember)
            .join(Organization, Organization.id == OrgMember.org_id)
            .where(
                Organization.tenant_id == tenant.id,
                # R68[2]: members of archived (deleted) orgs are not live
                # seats — without this filter a deleted org's students were
                # billed every period forever (delete_org now archives member
                # rows too, but the org filter also covers historic data).
                Organization.status != OrgStatus.ARCHIVED,
                OrgMember.status == MemberStatus.ACTIVE,
                OrgMember.role == OrgRole.STUDENT,
            )
        )
    ).scalar_one()
    # Use the PERIOD-START reserved floor, not the post-change sub.seat_quantity:
    # a mid-period immediate seat increase is billed by the proration line below,
    # so counting the raised floor here too double-charged the delta (R41[2]).
    # R82[M1]: when the seats line already bills the CURRENT live count for
    # the full period (live > start), a mid-period reserved-seat increase
    # must NOT also add its proration line — the live-count charge fully
    # covers the raised floor. Bill max(live, start); mark whether live won
    # so the proration walk skips the seat delta it would double-charge.
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

    # c. usage lines: un-invoiced rated usage grouped by type.
    # R43[14]: materialize the EXACT row set FIRST (id + amounts, FOR UPDATE)
    # and aggregate in Python — the old SUM-then-rebind ran two separate
    # queries, so a row rated between them was flipped to 'invoiced' by the
    # bind UPDATE without its amount ever being summed into the line (silently
    # billed 0). The lock also serializes against concurrent rating/settlement
    # touching these rows.
    from app.controlplane.models.usage import UsageEvent

    billable_rows = (
        await db.execute(
            select(
                RatedUsage.id,
                RatedUsage.usage_type,
                RatedUsage.billable_amount_exact,
                RatedUsage.quantity,
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
            .with_for_update(of=RatedUsage)
        )
    ).all()
    by_type: dict[str, dict] = {}
    for rid, utype, amount_exact, qty in billable_rows:
        agg = by_type.setdefault(utype, {"ids": [], "amount_exact": Decimal(0), "qty": Decimal(0)})
        agg["ids"].append(rid)
        # R75: round-of-sum — accumulate exact amounts, round ONCE per line.
        agg["amount_exact"] += Decimal(amount_exact or 0)
        agg["qty"] += Decimal(qty or 0)
    usage_line_ids: dict[str, list[str]] = {}
    for utype in sorted(by_type):
        agg = by_type[utype]
        amount = int(agg["amount_exact"].quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if amount == 0:
            continue
        line = InvoiceLine(
            invoice_id=invoice.id,
            line_type="usage",
            description=f"Usage: {utype.replace('_', ' ')}",
            quantity=agg["qty"],
            amount_minor=amount,
            usage_summary={
                "usage_type": utype,
                "event_count": len(agg["ids"]),
                "total_quantity": str(agg["qty"]),
                "period_start": period.period_start.isoformat(),
                "period_end": period.period_end.isoformat(),
            },
            sort_order=sort,
        )
        lines.append(line)
        usage_line_ids[utype] = agg["ids"]
        sort += 1
    for line in lines:
        db.add(line)
    await db.flush()
    # Bind EXACTLY the rows that were summed — by id, not by re-querying.
    for line in lines:
        if line.line_type != "usage":
            continue
        ids = usage_line_ids.get(line.usage_summary["usage_type"], [])
        if ids:
            await db.execute(
                update(RatedUsage)
                .where(RatedUsage.id.in_(ids), RatedUsage.status == "rated")
                .values(status="invoiced", invoice_line_id=line.id)
            )

    # d. license lines (bill_via_invoice purchases — P8 wires the flag)
    try:
        from app.controlplane.models.marketplace import MarketplacePurchase

        # R97[H8]: FOR UPDATE — this select raced refund_purchase (guarded
        # paid→refunded): the close read the purchase as 'paid', the refund
        # committed (license revoked), then the close billed the refunded
        # purchase anyway. The lock serializes: whoever wins excludes the row
        # from the loser (status predicate re-evaluated under the lock).
        pending_licenses = (
            (
                await db.execute(
                    select(MarketplacePurchase)
                    .where(
                        MarketplacePurchase.buyer_tenant_id == tenant.id,
                        MarketplacePurchase.status == "paid",
                        MarketplacePurchase.invoice_id.is_(None),
                        MarketplacePurchase.payment_method == "invoice",
                    )
                    .with_for_update()
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
    # R113[H7] (R101[H22] rework): the seat component is charged per SEGMENT
    # [change.effective_at → next change | period end), not per change over
    # ALL remaining days. The per-change walk both over-billed (an increase's
    # delta kept charging past a later decrease, and re-charged the
    # start→live band the base seats line already billed for the full period)
    # and — before H22 — under-billed. Per segment the tenant owes
    # max(floor, live, start) seats; the base line covers billable_seats
    # (= max(live, start)) for every day, so the segment extra is
    # max(floor − max(billable, included), 0). Plan-fee deltas still
    # telescope correctly per change via proration_preview (seat_price=0).
    total_period_days = max((period.period_end - period.period_start).days, 1)
    ordered_changes = sorted(changes, key=lambda c: (c.effective_at, c.id))
    for idx, change in enumerate(ordered_changes):
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
            seat_price_minor=0,  # seat component handled per segment below
        )
        seg_end = (
            ordered_changes[idx + 1].effective_at
            if idx + 1 < len(ordered_changes)
            else period.period_end
        )
        seg_days = max((min(seg_end, period.period_end) - change.effective_at).days, 0)
        seat_price = (new_p.overage_seat_amount_minor or 0) if new_p else 0
        seg_included = new_p.included_seats if new_p else 0
        covered = max(billable_seats, seg_included)
        extra_seats = max((change.to_seats or 0) - covered, 0)
        seat_minor = int(
            (Decimal(extra_seats * seat_price * seg_days) / Decimal(total_period_days)).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )
        net_minor = preview["net_minor"] + seat_minor
        if net_minor != 0:
            db.add(
                InvoiceLine(
                    invoice_id=invoice.id,
                    line_type="proration",
                    description=(
                        f"Plan change on {change.effective_at.date().isoformat()} "
                        f"({preview['days_left']} days remaining)"
                    ),
                    quantity=1,
                    amount_minor=net_minor,
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
    # func.sum on BigInteger yields Decimal — coerce, or the negative-carry
    # refund below feeds a Decimal into the audit JSONB (500 at close).
    subtotal = int(subtotal)
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

    # R113[M8]: on the sub's FINAL close (cancelled / cancel-at-end) no next
    # period is opened, so no future close will ever sweep this tenant again.
    # Usage rated AFTER the billable_rows lock above (rating isn't serialized
    # against the close) stays 'rated' forever — silently unbilled revenue.
    # Do NOT silently bill it here: its amounts were never summed into a line
    # and late-rated usage may need ops judgement on a dead account. Count and
    # warn so ops can review (manual invoice or write-off).
    if sub.status in ("cancel_at_period_end", "cancelled"):
        residual = (
            await db.execute(
                select(func.count(RatedUsage.id))
                .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
                .where(
                    RatedUsage.tenant_id == tenant.id,
                    RatedUsage.status == "rated",
                    RatedUsage.billable_currency == sub.currency,
                    UsageEvent.occurred_at < period.period_end,
                )
            )
        ).scalar_one()
        if residual:
            log.warning(
                "cp_final_close_residual_usage",
                subscription_id=sub.id,
                tenant_id=tenant.id,
                count=residual,
            )

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
            # R64[16]/R94[H4]: push the now-applied deferred change to the
            # provider — but NOT inline: this transaction holds the
            # Subscription FOR UPDATE, the GLOBAL InvoiceSequence lock and the
            # tenant's credit-balance lock; an un-timed Stripe HTTP call here
            # stalled EVERY concurrent invoice finalize platform-wide.
            # Decouple via the outbox (own retry/backoff; handler idempotent
            # — it pushes the sub's CURRENT state).
            if sub.provider in ("mock", "stripe") and sub.external_ref:
                enqueue(db, "subscription.push_provider", {"subscription_id": sub.id})

        next_start = period.period_end
        next_end = _add_interval(next_start, sub.interval)
        # R113[L5]: month-end anchor drift — a Jan-31 subscription rolls to
        # Feb-28, and clamping from the 28th keeps every later period on the
        # 28th forever. Restore the ORIGINAL anchor day when the target month
        # can hold it (created_at fixes the anchor for the sub's lifetime).
        if sub.interval == "month":
            anchor = sub.created_at.day
            max_day = _month_len(next_end.year, next_end.month)
            if anchor > next_end.day and anchor <= max_day:
                next_end = next_end.replace(day=min(anchor, max_day))
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
    # R43[13]: lock the invoice — two concurrent partial payments both read a
    # stale paid_total, both crossed the threshold, and the past_due→active
    # transition fired twice. FOR UPDATE serializes the sum + transition.
    invoice = (
        await db.execute(
            select(Invoice)
            .where(Invoice.id == invoice.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    if invoice.status not in ("open", "paid"):
        raise AppError("INVOICE_NOT_OPEN", "Invoice is not open for payment", 409)
    # R50[47]: uq_cp_payment_external (external_ref, method) is the provider
    # double-delivery guard — a duplicate manual entry hit it as an unhandled
    # IntegrityError 500. Pre-check and return a clean 409.
    if external_ref:
        dup = (
            await db.execute(
                select(PaymentRecord.id)
                .where(
                    PaymentRecord.external_ref == external_ref,
                    PaymentRecord.method == method,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if dup is not None:
            raise AppError(
                "PAYMENT_INVALID",
                f"A {method} payment with external_ref '{external_ref}' already exists",
                409,
            )
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
    # R43[8] CRITICAL: the close debited the tenant's credit balance for
    # credit_applied_minor and the void re-queues the same usage for the next
    # invoice — without refunding, the credit is permanently lost AND the usage
    # is billed again at full price (double charge). Refund exactly what was
    # applied (idempotent per invoice).
    if invoice.credit_applied_minor and invoice.credit_applied_minor > 0:
        await credit_svc.refund(
            db,
            invoice.tenant_id,
            invoice.currency,
            invoice.credit_applied_minor,
            reference_type="invoice",
            reference_id=invoice.id,
            reason="Credit returned on invoice void",
            actor=actor,
            idempotency_key=f"invvoid:{invoice.id}",
        )
    # R43[11]: unbind invoice-billed license purchases so the re-close can pick
    # them up again (their license line died with this invoice).
    try:
        from app.controlplane.models.marketplace import MarketplacePurchase

        await db.execute(
            update(MarketplacePurchase)
            .where(MarketplacePurchase.invoice_id == invoice.id)
            .values(invoice_id=None)
        )
    except ImportError:
        pass
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
        # R82[3]: the rewind assumes this is the sub's LATEST period — its
        # forward-delete removes every period starting at/after this one's
        # end WITHOUT a status filter, so voiding an OLDER open invoice
        # (disputed June voided in August) deleted July's already-INVOICED
        # (even PAID) period and re-billed it at the next close cycle —
        # double-charging every subsequent period. Rewind only when no later
        # non-open period exists; otherwise void plainly (usage rows were
        # already unbound above) and corrections go through credit notes.
        later_locked = None
        if period is not None:
            later_locked = (
                await db.execute(
                    select(BillingPeriod.id)
                    .where(
                        BillingPeriod.subscription_id == period.subscription_id,
                        BillingPeriod.period_start >= period.period_end,
                        BillingPeriod.status != "open",
                    )
                    .limit(1)
                )
            ).scalar_one_or_none()
        if period is not None and later_locked is not None:
            log.warning(
                "cp_void_no_rewind_later_period",
                invoice_id=invoice.id,
                period_id=period.id,
            )
        if period is not None and later_locked is None:
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
    # R43[13]/[10]: lock the invoice row — the cumulative cap below and
    # record_payment's paid-total check must not race concurrent notes/payments.
    invoice = (
        await db.execute(
            select(Invoice)
            .where(Invoice.id == invoice.id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    if invoice.status not in ("open", "paid"):
        raise AppError("INVOICE_NOT_OPEN", "Credit notes apply to finalized invoices", 409)
    if amount_minor <= 0 or amount_minor > invoice.total_minor:
        raise AppError("PAYMENT_INVALID", "Credit note exceeds invoice total", 422)
    # R43[10]: cap CUMULATIVELY — each note was only checked against the
    # invoice total, so N notes could refund N× the invoice.
    prior_notes = (
        await db.execute(
            select(func.coalesce(func.sum(CreditNote.amount_minor), 0)).where(
                CreditNote.invoice_id == invoice.id,
                CreditNote.status == "applied",
            )
        )
    ).scalar_one()
    if prior_notes + amount_minor > invoice.total_minor:
        raise AppError(
            "PAYMENT_INVALID",
            f"Credit notes may not exceed the invoice total "
            f"(already issued {prior_notes} of {invoice.total_minor})",
            422,
        )
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
    # R43[12]: on a still-OPEN (unpaid) invoice, the note reduces what the
    # tenant OWES — a ledger refund on top was a double benefit (debt reduced
    # AND spendable credit granted). The ledger refund is the correction
    # mechanism for money already COLLECTED.
    # R88[10]: but an open invoice may already have collected money — credit
    # applied at close (ledger debited) and/or partial payments. A note
    # larger than amount_due covers part of that COLLECTED money; silently
    # flooring at 0 kept it. Split: reduce the debt by min(note, due), and
    # refund the remainder (the collected portion) to the ledger.
    was_open = invoice.status == "open"
    refund_amount = amount_minor
    if was_open:
        # R101[C0]: amount_due_minor is set at finalize and never reduced by
        # record_payment (which only compares paid_total against it) — the true
        # outstanding debt is amount_due minus succeeded payments. Treating the
        # full amount_due as debt let a note "reduce" debt that was already
        # collected cash, silently keeping the collected portion.
        paid_total = (
            await db.execute(
                select(func.coalesce(func.sum(PaymentRecord.amount_minor), 0)).where(
                    PaymentRecord.invoice_id == invoice.id,
                    PaymentRecord.status == "succeeded",
                )
            )
        ).scalar_one()
        outstanding = max(invoice.amount_due_minor - int(paid_total), 0)
        debt_reduction = min(outstanding, amount_minor)
        refund_amount = amount_minor - debt_reduction
        invoice.amount_due_minor = invoice.amount_due_minor - debt_reduction
        if int(paid_total) >= invoice.amount_due_minor:
            await db.execute(
                update(Invoice)
                .where(Invoice.id == invoice.id, Invoice.status == "open")
                .values(status="paid", paid_at=_now())
            )
    await db.flush()
    if refund_amount > 0:  # collected money → refund as credit
        await credit_svc.refund(
            db,
            invoice.tenant_id,
            invoice.currency,
            refund_amount,
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
        # R42[7]: run the handler inside a SAVEPOINT (like the outbox worker)
        # so a DB-abort inside it (IntegrityError etc.) rolls back only the
        # handler's writes — NOT the just-inserted BillingWebhookEvent row.
        # Without it, the failed-status write below hit an aborted transaction,
        # the event row vanished with the rollback, and the provider's retry
        # re-processed a possibly half-applied event.
        async with db.begin_nested():
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


async def _notify_tenant_owners(
    db: AsyncSession, tenant_id: str, *, notification_type: str, title: str, body: str | None
) -> None:
    """R95[m10]: billing lifecycle events (payment failed, subscription
    cancelled by provider) were completely silent — the tenant discovered
    past_due only by noticing broken features. Notify tenant owners; a
    notification failure never fails the webhook (savepoint + swallow)."""
    try:
        async with db.begin_nested():
            from app.controlplane.models.tenant import TenantMember
            from app.services.notification import NotificationService

            owner_ids = (
                (
                    await db.execute(
                        select(TenantMember.user_id)
                        .where(
                            TenantMember.tenant_id == tenant_id,
                            TenantMember.role.in_(["owner", "billing_admin"]),
                        )
                        .limit(20)
                    )
                )
                .scalars()
                .all()
            )
            # R113[M4]: a tenant with no owner/billing_admin members made every
            # billing alert (payment failed, provider cancel) vanish silently —
            # the loop simply didn't run and nothing recorded that nobody was
            # told. Warn so ops can spot the unreachable tenant.
            if not owner_ids:
                log.warning(
                    "cp_notify_no_tenant_owners",
                    tenant_id=tenant_id,
                    type=notification_type,
                )
            svc = NotificationService(db)
            for uid in owner_ids:
                await svc.create(
                    user_id=uid,
                    notification_type=notification_type,
                    title=title,
                    body=body,
                )
    except Exception:  # noqa: BLE001
        log.warning("cp_billing_notify_failed", tenant_id=tenant_id, type=notification_type)


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
                pinned_version_id=meta.get("plan_version_id"),
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
            await _notify_tenant_owners(
                db,
                tenant.id,
                notification_type="billing.payment_failed",
                title="Payment failed — account is past due",
                body="A subscription payment failed. Update your payment method to avoid interruption.",
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
        # R101[H21]: same as the platform-initiated immediate cancel (R41[4]) —
        # 'cancelled' subs fall out of scan_due_periods, so the open period
        # holding the final partial plan fee + in-period usage would never be
        # closed or billed. Truncate to now and enqueue the close.
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
        # R113[M5]: a PROVIDER-initiated cancel (dunning exhausted, card
        # disputes, Stripe dashboard action) killed the subscription with zero
        # tenant-facing signal — payment_failed notifies (R95[m10]) but the
        # terminal event didn't, so the tenant discovered cancellation only
        # when features died. Same owner-notification path as payment_failed.
        await _notify_tenant_owners(
            db,
            sub.tenant_id,
            notification_type="billing.subscription_cancelled",
            title="Subscription cancelled",
            body=(
                "Your subscription was cancelled by the payment provider. "
                "A final invoice will be issued."
            ),
        )
        await invalidate_cache(sub.tenant_id)
        return True

    return False  # unknown event type → ignored (200, no retry storm)


@register_handler("subscription.push_provider")
async def handle_subscription_push_provider(db: AsyncSession, payload: dict) -> None:
    """R94[H4]: push the subscription's CURRENT plan/seats to the billing
    provider — decoupled from close_period_and_invoice so the un-timed
    provider HTTP call never runs while the close holds the Subscription,
    global InvoiceSequence and credit-balance locks. Idempotent: pushes
    current state; a duplicate push is a no-op provider-side."""
    sub = await db.get(Subscription, payload["subscription_id"])
    if sub is None or sub.provider not in ("mock", "stripe") or not sub.external_ref:
        return
    from app.controlplane.services.billing_providers import get_billing_provider

    adapter = get_billing_provider(sub.provider)
    if adapter is None:
        return
    new_p = (
        await db.execute(
            select(PlanPrice).where(
                PlanPrice.plan_version_id == sub.plan_version_id,
                PlanPrice.currency == sub.currency,
                PlanPrice.interval == sub.interval,
            )
        )
    ).scalar_one_or_none()
    if new_p is None:
        log.error(
            "cp_provider_change_push_no_price",
            subscription_id=sub.id,
            provider=sub.provider,
        )
        return
    # R101[M38]: a deferred change can land on a plan whose Stripe price ref
    # was never configured — pushing "" makes Stripe error on every retry
    # until dead-letter while the provider keeps billing the old price. This
    # is an ops-config gap, not a transient: log loudly and stop (the push is
    # re-enqueued by the next change once the ref exists, or replayed).
    if sub.provider == "stripe" and not new_p.external_price_ref:
        # R113[L14]: the M38 early-return dropped the CANCEL FLAG sync along
        # with the (impossible) price push. When the platform sub is pending
        # cancellation, at least sync that flag via the provider's cancel API
        # (needs no price ref) — otherwise Stripe kept auto-renewing a sub the
        # customer cancelled. The reverse (reactivate wanting the flag
        # CLEARED) cannot be synced without a price ref (Stripe clear is a
        # subscription modify); the loud error below covers that gap for ops.
        if sub.cancel_at_period_end:
            await adapter.cancel_subscription(sub.external_ref, at_period_end=True)
        log.error(
            "cp_provider_change_push_no_external_ref",
            subscription_id=sub.id,
            plan_version_id=sub.plan_version_id,
        )
        return
    # R98[30]: let failures RAISE — the outbox retries with backoff and
    # dead-letters visibly, instead of the old one-shot swallowed log line.
    # R113[C0]: push the PLATFORM row's cancel flag — the adapter previously
    # hardcoded cancel_at_period_end=False, so any push (plan/seat change,
    # deferred rollover) silently un-cancelled a pending Stripe cancellation.
    await adapter.change_subscription(
        sub.external_ref,
        new_p.external_price_ref or "",
        sub.seat_quantity,
        cancel_at_period_end=bool(sub.cancel_at_period_end),
    )


@register_handler("subscription.cancel_provider")
async def handle_subscription_cancel_provider(db: AsyncSession, payload: dict) -> None:
    """R113[M20/M34]: provider-side cancel decoupled from cancel_subscription —
    the inline call ran under the sub row lock and its failure rolled back the
    whole cancel (or committed a provider cancel the platform then forgot).
    Payload pins provider/external_ref as of cancel time, so a delayed retry
    cancels exactly the sub the customer cancelled — never a successor sub
    created by a later re-subscribe. Idempotent provider-side: cancelling an
    already-cancelled provider sub is a no-op/terminal error the adapter maps."""
    provider = payload.get("provider")
    external_ref = payload.get("external_ref")
    if provider not in ("mock", "stripe") or not external_ref:
        return
    from app.controlplane.services.billing_providers import get_billing_provider

    adapter = get_billing_provider(provider)
    if adapter is None:
        return
    # Failures RAISE — the outbox retries with backoff and dead-letters
    # visibly (mirrors handle_subscription_push_provider).
    await adapter.cancel_subscription(external_ref, bool(payload.get("at_period_end")))
