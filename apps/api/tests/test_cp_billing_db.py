"""P6 DB tests: subscription lifecycle, proration, invoice generation,
webhook replay, manual ops, concurrent finalize."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import func, select
from ulid import ULID

from app.controlplane.models.billing import (
    BillingPeriod,
    Invoice,
    InvoiceLine,
    Subscription,
)
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import billing as billing_svc
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus


@pytest.fixture
async def db():
    from app.core.database import engine

    # R134 follow-up: a preceding file can leave pool connections bound to its
    # (now closed) event loop — the first checkout here then dies with
    # "Event loop is closed". Abandon any stale pool without touching the
    # dead-loop connections (close=False), then open fresh ones on this loop.
    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db) -> User:
    user = User(
        email=f"cp6-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP6",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user, status=TenantStatus.TRIAL) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"B {ULID()}",
        slug=f"b-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=status,
        with_trial=(status == TenantStatus.TRIAL),
    )


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── Proration (pure, worked numbers from the plan §6.3) ──────


def test_proration_worked_example():
    """school $199 → growth $499, day 10 end of a 30-day period."""
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = datetime(2026, 10, 1, tzinfo=UTC)
    at = datetime(2026, 9, 11, tzinfo=UTC)  # 10 days used, 20 left
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=19900,
        new_amount_minor=49900,
    )
    assert p["total_days"] == 30
    assert p["days_left"] == 20
    assert p["credit_unused_old_minor"] == 13267  # 19900/30×20
    assert p["charge_new_remaining_minor"] == 33267  # 49900/30×20
    assert p["net_minor"] == 20000


def test_proration_boundaries_and_seats():
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = datetime(2026, 10, 1, tzinfo=UTC)
    # Change at period start: full-period swap
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=start,
        old_amount_minor=10000,
        new_amount_minor=20000,
    )
    assert p["net_minor"] == 10000
    # Change at period end: nothing left to prorate
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=end,
        old_amount_minor=10000,
        new_amount_minor=20000,
    )
    assert p["net_minor"] == 0
    # Seat increase mid-period
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=datetime(2026, 9, 16, tzinfo=UTC),
        old_amount_minor=0,
        new_amount_minor=0,
        old_seats=10,
        new_seats=20,
        seat_price_minor=500,
    )
    assert p["seat_proration_minor"] == 2500  # 10 seats × 500 × 15/30


def test_proration_downgrade_and_seat_decrease():
    # R16: downgrade → negative net → next_period_default mode
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = datetime(2026, 10, 1, tzinfo=UTC)
    at = datetime(2026, 9, 11, tzinfo=UTC)  # 20 days left of 30
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=49900,
        new_amount_minor=19900,
    )
    assert p["net_minor"] == -20000
    assert p["mode"] == "next_period_default"
    # Seat DECREASE must never produce a negative proration (max(delta,0))
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=19900,
        new_amount_minor=19900,
        old_seats=12,
        new_seats=0,
        seat_price_minor=500,
    )
    assert p["seat_proration_minor"] == 0
    # Clock skew: at < period_start clamps days_left to the full period, never > total
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=datetime(2026, 8, 20, tzinfo=UTC),
        old_amount_minor=19900,
        new_amount_minor=49900,
    )
    assert p["days_left"] == 30


# ── Lifecycle ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_manual_subscription_activates_trial_tenant(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    sub, url = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    assert url is None and sub.status == "active"
    await db.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE  # trial converted
    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    assert period.status == "open"
    # Second subscription rejected
    with pytest.raises(AppError) as exc:
        await billing_svc.start_subscription(
            db,
            tenant,
            plan_key="growth",
            interval="month",
            seats=0,
            provider="manual",
            actor=_actor(user),
        )
    assert exc.value.code == "SUBSCRIPTION_EXISTS"


@pytest.mark.asyncio
async def test_plan_change_and_cancel(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    result = await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key="growth",
        seats=None,
        proration_mode=None,
        actor=_actor(user),
    )
    assert result["mode"] == "immediate"  # upgrade defaults immediate
    await db.refresh(sub)
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    version = await db.get(PlanVersion, sub.plan_version_id)
    plan = await db.get(ProductPlan, version.plan_id)
    assert plan.key == "growth"
    # Downgrade defaults next_period (plan stays until period end)
    result = await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key="school",
        seats=None,
        proration_mode=None,
        actor=_actor(user),
    )
    assert result["mode"] == "next_period"
    await db.refresh(sub)
    version = await db.get(PlanVersion, sub.plan_version_id)
    plan = await db.get(ProductPlan, version.plan_id)
    assert plan.key == "growth"  # unchanged until period close
    # Cancel at period end
    sub = await billing_svc.cancel_subscription(
        db, tenant, sub, at_period_end=True, actor=_actor(user)
    )
    assert sub.status == "cancel_at_period_end"


async def _force_close(db, sub) -> "Invoice | None":
    """Close the sub's open period → returns the invoice.

    Does NOT truncate period_end: close_period_and_invoice doesn't check
    due-ness, and truncating below a change's effective_at (next_period changes
    are stamped at the ORIGINAL future period_end) would break the arrears +
    proration ordering that holds in production, where close runs exactly when
    the period naturally ends."""
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    return await billing_svc.close_period_and_invoice(db, period.id)


def _plan_lines_total(lines, *types):
    return sum(line.amount_minor for line in lines if line.line_type in types)


async def _lines(db, invoice):
    return (
        (
            await db.execute(
                select(InvoiceLine)
                .where(InvoiceLine.invoice_id == invoice.id)
                .order_by(InvoiceLine.sort_order)
            )
        )
        .scalars()
        .all()
    )


@pytest.mark.asyncio
async def test_next_period_downgrade_actually_applies(db):
    """R41[0] CRITICAL: a next_period downgrade must take effect at rollover.
    Previously the SubscriptionChange was recorded but never applied — the sub
    kept billing the old (higher) plan every subsequent period."""
    from app.controlplane.models.plan import PlanVersion, ProductPlan

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    res = await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=None, proration_mode=None, actor=a
    )
    assert res["mode"] == "next_period"
    await db.refresh(sub)
    # Still growth until rollover.
    v = await db.get(PlanVersion, sub.plan_version_id)
    assert (await db.get(ProductPlan, v.plan_id)).key == "growth"
    # Close the period → the downgrade must now be applied to the sub.
    inv = await _force_close(db, sub)
    assert inv is not None
    await db.refresh(sub)
    v = await db.get(PlanVersion, sub.plan_version_id)
    assert (await db.get(ProductPlan, v.plan_id)).key == "school", (
        "next_period downgrade not applied"
    )
    # The closed period billed the OLD (growth) plan in arrears: 49900.
    assert _plan_lines_total(await _lines(db, inv), "plan") == 49900
    # Next period now bills school.
    inv2 = await _force_close(db, sub)
    assert _plan_lines_total(await _lines(db, inv2), "plan") == 19900


@pytest.mark.asyncio
async def test_immediate_upgrade_no_double_charge(db):
    """R41[1] CRITICAL: a mid-period immediate upgrade must bill the period-start
    (old) plan in arrears PLUS a single proration delta — not the new plan's
    full-period price AND the proration (which double-charged new−old)."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    # Immediate upgrade school→growth mid-period.
    res = await billing_svc.change_plan(
        db, tenant, sub, plan_key="growth", seats=None, proration_mode="immediate", actor=a
    )
    assert res["mode"] == "immediate"
    inv = await _force_close(db, sub)
    lines = await _lines(db, inv)
    plan_total = _plan_lines_total(lines, "plan")
    proration_total = _plan_lines_total(lines, "proration")
    # Plan line must be the OLD school price (arrears on period-start plan).
    assert plan_total == 19900, f"plan line should be old plan 19900, got {plan_total}"
    # There is a proration line (net upgrade delta ≥ 0). The invoice must NOT
    # contain growth's full 49900 as the plan line.
    assert plan_total != 49900
    # Total plan+proration is bounded by a full-period growth charge (49900) —
    # never old-full + full-delta (which exceeded it under the bug).
    assert plan_total + proration_total <= 49900 + 1, (plan_total, proration_total)


@pytest.mark.asyncio
async def test_void_reopens_period_and_uninvoices_changes(db):
    """R41[3]: voiding a period invoice must reopen the period and un-invoice
    its SubscriptionChanges so the next close regenerates the full invoice —
    not silently drop the plan fee + proration."""
    from app.controlplane.models.billing import SubscriptionChange

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="growth", seats=None, proration_mode="immediate", actor=a
    )
    inv = await _force_close(db, sub)
    assert inv is not None
    # The immediate change was consumed by this invoice.
    chg = (
        await db.execute(
            select(SubscriptionChange).where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.change_type == "plan_change",
            )
        )
    ).scalar_one()
    assert chg.invoiced is True
    period_id = inv.billing_period_id
    # Void the invoice before payment.
    await billing_svc.void_invoice(db, inv, reason="billing error", actor=a)
    await db.refresh(chg)
    period = await db.get(BillingPeriod, period_id)
    assert period.status == "open", "voided invoice must reopen its period"
    assert chg.invoiced is False, "voided invoice must un-invoice its changes"
    # Re-closing regenerates a full invoice (plan fee present again).
    inv2 = await billing_svc.close_period_and_invoice(db, period_id)
    assert inv2 is not None and inv2.id != inv.id
    assert _plan_lines_total(await _lines(db, inv2), "plan") == 19900


@pytest.mark.asyncio
async def test_immediate_cancel_bills_final_period(db):
    """R41[4]: an immediate cancel must close + bill the current partial period
    (via an enqueued period.close_due), not strand it open forever."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=False, actor=a)
    await db.refresh(sub)
    assert sub.status == "cancelled"
    # A period.close_due was enqueued for THIS sub's period (scope the check —
    # other tests' committed outbox rows are visible in a shared DB).
    my_period = (
        await db.execute(select(BillingPeriod.id).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    msg = (
        (await db.execute(select(OutboxMessage).where(OutboxMessage.topic == "period.close_due")))
        .scalars()
        .all()
    )
    mine = [m for m in msg if m.payload.get("billing_period_id") == my_period]
    assert mine, "immediate cancel must enqueue a final period close"
    period_id = mine[-1].payload["billing_period_id"]
    inv = await billing_svc.close_period_and_invoice(db, period_id)
    assert inv is not None, "final partial period must be billable"
    # No new open period is created for a cancelled sub.
    open_periods = (
        await db.execute(
            select(func.count(BillingPeriod.id)).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    assert open_periods == 0


# ── Invoice generation ───────────────────────────────────────


@pytest.mark.asyncio
async def test_period_close_generates_invoice_lines(db):
    from app.controlplane.services import metering, rating
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 5000, actor=a)  # $50 credit
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    # Tenant-priced usage: 10 images × 30 minor = 300
    await pricing_svc.create_price_policy(
        db,
        actor=a,
        name=f"inv {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 30},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    # Consumption must fall INSIDE the (soon force-closed) period window
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=10,
        occurred_at=datetime.now(UTC) - timedelta(minutes=5),
        source="manual",
        idempotency_key=f"inv-{ULID()}",
    )
    await rating.rate_event(db, event.id)
    # Force the period due and close it
    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    # Window ending "now" that is LONGER than one natural month: R82[2]'s
    # truncation proration only fires when actual < natural, so a normal
    # (non-truncated) close keeps the full fee, and in-window usage
    # (occurred minutes ago) still bills here.
    period.period_start = datetime.now(UTC) - timedelta(days=32)
    period.period_end = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None
    assert invoice.status in ("open", "paid")
    assert invoice.number and invoice.number.startswith("INV-")
    lines = (
        (
            await db.execute(
                select(InvoiceLine)
                .where(InvoiceLine.invoice_id == invoice.id)
                .order_by(InvoiceLine.sort_order)
            )
        )
        .scalars()
        .all()
    )
    types = [line.line_type for line in lines]
    assert "plan" in types and "usage" in types and "credit" in types
    plan_line = next(line for line in lines if line.line_type == "plan")
    assert plan_line.amount_minor == 19900
    usage_line = next(line for line in lines if line.line_type == "usage")
    assert usage_line.amount_minor == 300
    assert usage_line.usage_summary["event_count"] == 1
    # subtotal 20200, credit 5000 applied → due 15200
    assert invoice.subtotal_minor == 20200
    assert invoice.credit_applied_minor == 5000
    assert invoice.amount_due_minor == 15200
    # Rated row marked invoiced + bound to the line
    from app.controlplane.models.pricing import RatedUsage

    rated = (
        await db.execute(select(RatedUsage).where(RatedUsage.usage_event_id == event.id))
    ).scalar_one()
    assert rated.status == "invoiced" and rated.invoice_line_id == usage_line.id
    # Next period rolled
    next_period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    assert next_period.period_start == period.period_end
    # Idempotent: closing again is a no-op
    again = await billing_svc.close_period_and_invoice(db, period.id)
    assert again is None


@pytest.mark.asyncio
async def test_invoice_excludes_foreign_currency_usage_and_credit(db):
    """R21: a USD invoice bills ONLY USD-currency rated rows and applies ONLY
    USD credit — a foreign (EUR) rated row or credit balance never leaks in."""
    from decimal import Decimal

    from ulid import ULID as _ULID

    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    org = "01JFAKEORGFAKEORGFAKEORGFA"
    now = datetime.now(UTC) - timedelta(minutes=5)

    async def seed(billable, currency):
        eid = str(_ULID())
        db.add(
            UsageEvent(
                id=eid,
                tenant_id=tenant.id,
                org_id=org,
                usage_type="image_generation",
                quantity=Decimal(1),
                unit="images",
                occurred_at=now,
                source="manual",
            )
        )
        await db.flush()
        db.add(
            RatedUsage(
                usage_event_id=eid,
                tenant_id=tenant.id,
                org_id=org,
                usage_type="image_generation",
                quantity=Decimal(1),
                cost_rate_snapshot={},
                internal_cost_minor=0,
                internal_cost_currency="USD",
                sell_rate_snapshot={},
                billable_amount_minor=billable,
                billable_amount_exact=Decimal(billable),
                billable_currency=currency,
                status="rated",
                rated_at=now,
            )
        )
        await db.flush()

    await seed(300, "USD")  # bills
    await seed(999, "EUR")  # must not bill
    await credit_svc.top_up(db, tenant.id, "EUR", 100000, actor=a)  # must not apply

    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    # Window ending "now" that is LONGER than one natural month: R82[2]'s
    # truncation proration only fires when actual < natural, so a normal
    # (non-truncated) close keeps the full fee, and in-window usage
    # (occurred minutes ago) still bills here.
    period.period_start = datetime.now(UTC) - timedelta(days=32)
    period.period_end = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None and invoice.currency == "USD"
    lines = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    usage_total = sum(line.amount_minor for line in lines if line.line_type == "usage")
    assert usage_total == 300, usage_total  # EUR 999 excluded
    assert not [line for line in lines if line.line_type == "credit"]  # EUR credit not applied
    # EUR rated row remains unbilled
    eur = (
        await db.execute(
            select(RatedUsage).where(
                RatedUsage.tenant_id == tenant.id, RatedUsage.billable_currency == "EUR"
            )
        )
    ).scalar_one()
    assert eur.status == "rated"


@pytest.mark.asyncio
async def test_finalized_invoice_immutable_and_credit_note(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    invoice = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        provider="manual",
        subtotal_minor=1000,
        total_minor=1000,
        amount_due_minor=1000,
    )
    db.add(invoice)
    await db.flush()
    await billing_svc.finalize_invoice(db, invoice, actor=_actor(user))
    with pytest.raises(AppError) as exc:
        billing_svc.require_mutable(invoice)
    assert exc.value.code == "INVOICE_FINALIZED"
    # Double-finalize rejected
    with pytest.raises(AppError):
        await billing_svc.finalize_invoice(db, invoice, actor=_actor(user))
    # Payment marks paid + credit note refunds via ledger
    await billing_svc.record_payment(
        db,
        invoice,
        amount_minor=1000,
        method="manual_bank_transfer",
        external_ref=f"BANK-{ULID()}",
        reference_note="wire",
        received_at=None,
        actor=_actor(user),
    )
    await db.refresh(invoice)
    assert invoice.status == "paid"
    note = await billing_svc.issue_credit_note(
        db, invoice, amount_minor=400, reason="SLA breach credit", actor=_actor(user)
    )
    assert note.status == "applied"
    from app.controlplane.models.credit import TenantCreditBalance

    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.balance_minor == 400


@pytest.mark.asyncio
async def test_concurrent_finalize_single_number():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user, status=TenantStatus.ACTIVE)
            invoice = Invoice(
                tenant_id=tenant.id,
                currency="USD",
                provider="manual",
                subtotal_minor=500,
                total_minor=500,
                amount_due_minor=500,
            )
            setup.add(invoice)
            await setup.commit()
            inv_id, uid = invoice.id, user.id

        async def finalize():
            async with AsyncSessionLocal() as s:
                inv = await s.get(Invoice, inv_id)
                u = await s.get(User, uid)
                try:
                    await billing_svc.finalize_invoice(s, inv, actor=_actor(u))
                    await s.commit()
                    return True
                except Exception:
                    await s.rollback()
                    return False

        results = await asyncio.gather(finalize(), finalize())
        assert sorted(results) == [False, True]  # exactly one winner
        async with AsyncSessionLocal() as s:
            inv = await s.get(Invoice, inv_id)
            assert inv.number is not None
    finally:
        await engine.dispose()


# ── Webhooks ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mock_webhook_replay_single_effect(db):
    from app.controlplane.services.billing_providers.mock import sign_mock_event

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    event_id = f"mevt_{ULID()}"
    payload = {
        "id": event_id,
        "type": "checkout.completed",
        "data": {
            "id": f"mock_sess_{ULID()}",
            "amount_total": 2500,
            "metadata": {"tenant_id": tenant.id, "kind": "credit_topup"},
        },
    }
    raw, sig = sign_mock_event(payload)
    headers = {"x-mock-signature": sig}
    r1 = await billing_svc.process_webhook(db, "mock", headers, raw)
    assert r1["duplicate"] is False and r1["status"] == "processed"
    r2 = await billing_svc.process_webhook(db, "mock", headers, raw)
    assert r2["duplicate"] is True  # replay short-circuits
    from app.controlplane.models.credit import TenantCreditBalance

    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.balance_minor == 2500  # single effect


@pytest.mark.asyncio
async def test_webhook_bad_signature_rejected_not_stored(db):
    from app.controlplane.models.billing import BillingWebhookEvent

    before = (await db.execute(select(func.count(BillingWebhookEvent.id)))).scalar_one()
    with pytest.raises(AppError) as exc:
        await billing_svc.process_webhook(
            db, "mock", {"x-mock-signature": "forged"}, b'{"id": "evil", "type": "x"}'
        )
    assert exc.value.code == "WEBHOOK_SIGNATURE_INVALID"
    after = (await db.execute(select(func.count(BillingWebhookEvent.id)))).scalar_one()
    assert after == before  # nothing stored


@pytest.mark.asyncio
async def test_webhook_subscription_checkout_activates(db):
    from app.controlplane.services.billing_providers.mock import sign_mock_event

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    payload = {
        "id": f"mevt_{ULID()}",
        "type": "checkout.completed",
        "data": {
            "id": f"mock_sess_{ULID()}",
            "customer": f"mock_cus_{tenant.id}",
            "subscription": f"mock_sub_{ULID()}",
            "metadata": {
                "tenant_id": tenant.id,
                "kind": "subscription",
                "plan_key": "school",
                "interval": "month",
                "seats": "5",
            },
        },
    }
    raw, sig = sign_mock_event(payload)
    result = await billing_svc.process_webhook(db, "mock", {"x-mock-signature": sig}, raw)
    assert result["status"] == "processed"
    sub = await billing_svc.get_live_subscription(db, tenant.id)
    assert sub is not None and sub.status == "active" and sub.provider == "mock"
    await db.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE


# ── Stripe thin-wrapper webhook verification ─────────────────


def test_stripe_webhook_signature_with_fake_secret(monkeypatch):
    import json
    import time

    from app.config import settings as app_settings
    from app.controlplane.services.billing_providers.stripe import StripeProvider

    monkeypatch.setattr(app_settings, "stripe_webhook_secret", "whsec_test123")
    payload = json.dumps(
        {"id": "evt_1", "type": "invoice.paid", "data": {"object": {"subscription": "sub_1"}}}
    ).encode()
    ts = str(int(time.time()))
    import hashlib
    import hmac as hmac_mod

    signed_payload = f"{ts}.{payload.decode()}"
    sig = hmac_mod.new(b"whsec_test123", signed_payload.encode(), hashlib.sha256).hexdigest()
    header = f"t={ts},v1={sig}"
    parsed = StripeProvider().verify_webhook({"stripe-signature": header}, payload)
    assert parsed.external_event_id == "evt_1"
    assert parsed.event_type == "invoice.paid"
    # Tampered body fails
    with pytest.raises(AppError):
        StripeProvider().verify_webhook({"stripe-signature": header}, payload + b"tampered")


# ── R20: Stripe adapter param assembly + response mapping (thin wrapper) ──
# Fully monkeypatched SDK — asserts exact params sent and fields mapped back,
# so a wrong key/mode/price-ref can't silently reach Stripe.


def test_stripe_checkout_and_subscription_mapping(monkeypatch):
    import types

    from app.config import settings as app_settings
    from app.controlplane.services.billing_providers.stripe import StripeProvider

    monkeypatch.setattr(app_settings, "stripe_secret_key", "sk_test_x")
    calls: dict = {}

    def cap(name, ret):
        def f(*a, **kw):
            calls[name] = {"args": a, "kwargs": kw}
            return ret

        return f

    fake = types.ModuleType("stripe")
    fake.api_key = None
    fake.Customer = types.SimpleNamespace(create=cap("customer", {"id": "cus_1"}))
    fake.checkout = types.SimpleNamespace(
        Session=types.SimpleNamespace(
            create=cap("checkout", {"id": "cs_1", "url": "https://pay"}),
            retrieve=cap("session", {"payment_status": "paid"}),
        )
    )
    fake.Subscription = types.SimpleNamespace(
        retrieve=cap("sub_get", {"items": {"data": [{"id": "si_1"}]}}),
        modify=cap("sub_mod", {"id": "sub_1"}),
        cancel=cap("sub_cancel", {"id": "sub_1"}),
    )
    monkeypatch.setitem(__import__("sys").modules, "stripe", fake)

    p = StripeProvider()
    tenant = types.SimpleNamespace(id="01TENANT", name="Acme", billing_email="a@b.c")

    async def run():
        assert (await p.create_customer(tenant)) == "cus_1"
        assert calls["customer"]["kwargs"]["metadata"]["tenant_id"] == "01TENANT"

        price = types.SimpleNamespace(external_price_ref="price_abc")
        cs = await p.create_checkout_session(
            tenant=tenant,
            kind="subscription",
            plan_price=price,
            currency="USD",
            success_url="https://s",
            cancel_url="https://c",
        )
        assert cs.url == "https://pay" and cs.session_ref == "cs_1"
        kw = calls["checkout"]["kwargs"]
        assert kw["mode"] == "subscription"
        assert kw["line_items"][0]["price"] == "price_abc"

        # subscription checkout with no price ref → 409, never sent
        with pytest.raises(AppError) as exc:
            await p.create_checkout_session(
                tenant=tenant,
                kind="subscription",
                plan_price=types.SimpleNamespace(external_price_ref=None),
                currency="USD",
                success_url="https://s",
                cancel_url="https://c",
            )
        assert exc.value.code == "PLAN_NOT_AVAILABLE"

        # one-off top-up assembles price_data with lowercased currency
        await p.create_checkout_session(
            tenant=tenant,
            kind="credit_topup",
            amount_minor=5000,
            currency="USD",
            success_url="https://s",
            cancel_url="https://c",
        )
        kw2 = calls["checkout"]["kwargs"]
        assert kw2["mode"] == "payment"
        assert kw2["line_items"][0]["price_data"]["unit_amount"] == 5000
        assert kw2["line_items"][0]["price_data"]["currency"] == "usd"

        # R291: a one-off payment with no/zero amount must be a clean 422 at
        # the boundary (amount_minor is typed int|None) — NOT Decimal(None)
        # → TypeError 500 inside _stripe_unit_amount. The SDK is never called.
        calls.pop("checkout", None)
        for bad in (None, 0, -100):
            with pytest.raises(AppError) as exc_amt:
                await p.create_checkout_session(
                    tenant=tenant, kind="credit_topup", amount_minor=bad,
                    currency="USD", success_url="https://s", cancel_url="https://c")
            assert exc_amt.value.code == "VALIDATION_ERROR"
            assert exc_amt.value.status_code == 422
        assert "checkout" not in calls          # guard fired before the SDK call

        # change reuses retrieved item id + disables Stripe-side proration
        await p.change_subscription("sub_1", "price_new", 5)
        mk = calls["sub_mod"]["kwargs"]
        assert mk["items"][0]["id"] == "si_1"
        assert mk["items"][0]["price"] == "price_new"
        assert mk["proration_behavior"] == "none"

        # cancel routing
        await p.cancel_subscription("sub_1", at_period_end=True)
        assert calls["sub_mod"]["kwargs"].get("cancel_at_period_end") is True
        await p.cancel_subscription("sub_1", at_period_end=False)
        assert "sub_cancel" in calls

        assert (await p.fetch_payment_status("cs_1")) == "paid"

    import asyncio

    asyncio.get_event_loop().run_until_complete(run()) if False else asyncio.run(run())


def test_stripe_unit_amount_currency_convention():
    """R75[15]: the platform stores money as major×minor_multiplier (×1 for
    JPY/KRW, ×100 otherwise), but Stripe's smallest-unit convention differs —
    VND-class is zero-decimal, KWD-class three-decimal. The boundary must
    convert both ways so a top-up isn't 100× over- or 10× under-charged."""
    from app.controlplane.services.billing_providers.stripe import (
        _platform_minor_from_stripe,
        _stripe_unit_amount,
    )

    # USD: platform 5000 minor ($50.00) → Stripe 5000 (two-decimal) → back 5000.
    assert _stripe_unit_amount(5000, "USD") == 5000
    assert _platform_minor_from_stripe(5000, "USD") == 5000
    # VND (zero-decimal on Stripe): platform stores 1000.00 VND as 100000 minor
    # (×100 default), Stripe wants 1000 → not 100000 (the 100× overcharge).
    assert _stripe_unit_amount(100000, "VND") == 1000
    assert _platform_minor_from_stripe(1000, "VND") == 100000
    # KWD (three-decimal on Stripe): platform 10.00 KWD = 1000 minor (×100),
    # Stripe wants 10000 → not 1000 (the 10× undercharge).
    assert _stripe_unit_amount(1000, "KWD") == 10000
    assert _platform_minor_from_stripe(10000, "KWD") == 1000
    # JPY (zero-decimal both sides): platform 500 minor (×1) → Stripe 500.
    assert _stripe_unit_amount(500, "JPY") == 500
    assert _platform_minor_from_stripe(500, "JPY") == 500


@pytest.mark.asyncio
async def test_negative_invoice_balance_carried_forward_as_credit(db):
    """R75[14]: a net-negative period subtotal (large immediate-downgrade
    credit) is money owed to the tenant — it must be refunded to the credit
    ledger, not clamped to 0 and lost."""
    from app.controlplane.models.credit import TenantCreditBalance

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    # Start on growth, immediately downgrade to community (free) near period
    # start → a large negative proration credit dwarfs the tiny arrears.
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="community", seats=None, proration_mode="immediate", actor=a
    )
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    inv = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv is not None
    # amount_due clamped at 0 (can't owe a negative), but the residual credit
    # landed in the ledger as a refund carry-forward.
    assert inv.amount_due_minor == 0
    if inv.subtotal_minor < 0:
        bal = (
            await db.execute(
                select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
            )
        ).scalar_one_or_none()
        assert bal is not None
        assert bal.balance_minor == -inv.subtotal_minor, (
            f"residual {-inv.subtotal_minor} not carried forward, balance={bal.balance_minor}"
        )


# ── R64: billing-provider correctness ─────────────────────────


def test_subscription_ref_tolerates_basil_payloads():
    """R64[19]: Stripe API 2025-03+ moved Invoice.subscription to
    parent.subscription_details.subscription — read both shapes."""
    from app.controlplane.services.billing import _subscription_ref

    assert _subscription_ref({"subscription": "sub_1"}) == "sub_1"
    assert _subscription_ref({"subscription": {"id": "sub_2"}}) == "sub_2"
    assert (
        _subscription_ref({"parent": {"subscription_details": {"subscription": "sub_3"}}})
        == "sub_3"
    )
    assert (
        _subscription_ref({"parent": {"subscription_details": {"subscription": {"id": "sub_4"}}}})
        == "sub_4"
    )
    assert _subscription_ref({}) is None


def test_mock_webhook_non_ascii_signature_is_401_not_500():
    """R64[20]: hmac.compare_digest raises TypeError on non-ASCII str — an
    unauthenticated request with a latin-1 header must 401, not 500."""
    from app.controlplane.services.billing_providers.mock import MockProvider

    with pytest.raises(AppError) as exc:
        MockProvider().verify_webhook({"x-mock-signature": "\xff\xff"}, b"{}")
    assert exc.value.code == "WEBHOOK_SIGNATURE_INVALID"
    assert exc.value.status_code == 401


@pytest.mark.asyncio
async def test_unpaid_checkout_session_delivers_nothing(db):
    """R64[15]: checkout.session.completed with payment_status='unpaid'
    (SEPA/ACH/boleto) must NOT deliver credits — delivery waits for
    async_payment_succeeded."""
    from types import SimpleNamespace

    from app.controlplane.models.credit import TenantCreditBalance
    from app.controlplane.services.billing import _apply_webhook_event

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    parsed = SimpleNamespace(
        event_type="checkout.session.completed",
        data={
            "id": "cs_unpaid_1",
            "payment_status": "unpaid",
            "amount_total": 5000,
            "metadata": {"tenant_id": tenant.id, "kind": "credit_topup"},
        },
    )
    handled = await _apply_webhook_event(db, "stripe", parsed)
    assert handled is True  # recorded, not an error
    bal = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    assert bal is None or bal.balance_minor == 0, "unpaid session must not credit"
    # The async success event later delivers.
    parsed2 = SimpleNamespace(
        event_type="checkout.session.async_payment_succeeded",
        data={
            "id": "cs_unpaid_1",
            "payment_status": "paid",
            "amount_total": 5000,
            "metadata": {"tenant_id": tenant.id, "kind": "credit_topup"},
        },
    )
    await _apply_webhook_event(db, "stripe", parsed2)
    bal2 = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert bal2.balance_minor == 5000


@pytest.mark.asyncio
async def test_invoice_paid_reactivates_subscription_not_just_tenant(db):
    """R64/R42[6]: invoice.paid must flip the SUBSCRIPTION out of past_due too,
    not only the tenant — else the sub is permanently stuck."""
    from types import SimpleNamespace

    from app.controlplane.models.billing import Subscription
    from app.controlplane.services.billing import _apply_webhook_event

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    sub.provider = "stripe"
    sub.external_ref = "sub_pd_1"
    sub.status = "past_due"
    await db.flush()
    parsed = SimpleNamespace(
        event_type="invoice.paid",
        data={"subscription": "sub_pd_1", "metadata": {}},
    )
    handled = await _apply_webhook_event(db, "stripe", parsed)
    assert handled is True
    refreshed = await db.get(Subscription, sub.id)
    await db.refresh(refreshed)
    assert refreshed.status == "active", refreshed.status


@pytest.mark.asyncio
async def test_duplicate_checkout_cancels_orphan_provider_subscription(db, monkeypatch):
    """R64[17]: a second completed checkout session for a tenant that already
    has a live subscription must cancel the orphan provider-side subscription
    (it would double-bill with no platform record)."""
    from app.controlplane.services import billing as bsvc
    from app.controlplane.services.billing import activate_subscription_from_checkout
    from app.controlplane.services.billing_providers.mock import MockProvider

    cancelled: list = []

    async def fake_cancel(self, external_ref, at_period_end):
        cancelled.append((external_ref, at_period_end))

    monkeypatch.setattr(MockProvider, "cancel_subscription", fake_cancel)
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    first = await activate_subscription_from_checkout(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="mock",
        external_customer_ref="cus_1",
        external_ref="mock_sub_1",
    )
    assert first.external_ref == "mock_sub_1"
    # Second completed session with a DIFFERENT provider subscription ref.
    again = await activate_subscription_from_checkout(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="mock",
        external_customer_ref="cus_1",
        external_ref="mock_sub_2",
    )
    assert again.id == first.id  # platform keeps the first
    assert cancelled == [("mock_sub_2", False)], cancelled
    _ = bsvc  # keep import for clarity


# ── R42/R43: invoice lifecycle correctness ────────────────────


@pytest.mark.asyncio
async def test_void_refunds_applied_credit(db):
    """R43[8] CRITICAL: voiding an invoice that consumed credit must refund
    the applied credit — the usage re-bills next cycle, so losing the credit
    was a double charge."""
    from app.controlplane.models.credit import TenantCreditBalance
    from app.controlplane.services import metering, rating
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 5000, actor=a)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await pricing_svc.create_price_policy(
        db,
        actor=a,
        name=f"v8 {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 30},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    ev = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=10,
        occurred_at=datetime.now(UTC) - timedelta(minutes=5),
        source="manual",
        idempotency_key=f"v8-{ULID()}",
    )
    await rating.rate_event(db, ev.id)
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    inv = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv is not None and inv.credit_applied_minor == 5000
    bal = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert bal.balance_minor == 0  # consumed by the close
    await billing_svc.void_invoice(db, inv, reason="billing error", actor=a)
    await db.refresh(bal)
    assert bal.balance_minor == 5000, "voided credit must be refunded"


@pytest.mark.asyncio
async def test_credit_note_cumulative_cap_and_open_invoice_reduces_due(db):
    """R43[10]+[12]: notes cap CUMULATIVELY at the invoice total, and a note on
    an OPEN invoice reduces amount_due (no ledger refund — that would be a
    double benefit)."""
    from app.controlplane.models.credit import TenantCreditBalance

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    # Manual open invoice of 10000.
    inv = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        status="open",
        subtotal_minor=10000,
        total_minor=10000,
        amount_due_minor=10000,
        finalized_at=datetime.now(UTC),
    )
    db.add(inv)
    await db.flush()
    n1 = await billing_svc.issue_credit_note(
        db, inv, amount_minor=6000, reason="partial dispute", actor=a
    )
    assert n1 is not None
    await db.refresh(inv)
    assert inv.amount_due_minor == 4000  # reduced, not refunded
    bal = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one_or_none()
    assert bal is None or bal.balance_minor == 0, "open-invoice note must not refund ledger"
    # Cumulative cap: 6000 issued of 10000 → a 5000 second note exceeds it.
    with pytest.raises(AppError) as exc:
        await billing_svc.issue_credit_note(db, inv, amount_minor=5000, reason="too much", actor=a)
    assert exc.value.code == "PAYMENT_INVALID"
    # 4000 exactly reaches the cap and closes the invoice as paid.
    await billing_svc.issue_credit_note(db, inv, amount_minor=4000, reason="rest", actor=a)
    await db.refresh(inv)
    assert inv.amount_due_minor == 0 and inv.status == "paid"


@pytest.mark.asyncio
async def test_duplicate_external_ref_payment_409_not_500(db):
    """R50[47]: a duplicate (external_ref, method) manual payment must be a
    clean 409, not an unhandled unique-violation 500."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    inv = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        status="open",
        subtotal_minor=10000,
        total_minor=10000,
        amount_due_minor=10000,
        finalized_at=datetime.now(UTC),
    )
    db.add(inv)
    await db.flush()
    await billing_svc.record_payment(
        db,
        inv,
        amount_minor=5000,
        method="manual_bank_transfer",
        external_ref=f"wire-{inv.id}",
        reference_note=None,
        received_at=None,
        actor=a,
    )
    with pytest.raises(AppError) as exc:
        await billing_svc.record_payment(
            db,
            inv,
            amount_minor=5000,
            method="manual_bank_transfer",
            external_ref=f"wire-{inv.id}",
            reference_note=None,
            received_at=None,
            actor=a,
        )
    assert exc.value.code == "PAYMENT_INVALID" and exc.value.status_code == 409


@pytest.mark.asyncio
async def test_archived_org_students_not_billed_as_seats(db):
    """R68[2]: the invoice seats line counted ACTIVE members of ARCHIVED
    (deleted) orgs — a deleted org's students were billed every period
    forever. The live-seats query must exclude archived orgs."""
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
        OrgStatus,
    )

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    # An ARCHIVED org with 205 historic ACTIVE member rows (pre-fix debris) —
    # above the school plan's 200 included seats, so counting them WOULD
    # produce an overage line.
    org = Organization(
        name=f"Dead {ULID()}",
        slug=f"dead-{str(ULID()).lower()}",
        tenant_id=tenant.id,
        status=OrgStatus.ARCHIVED,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    for _ in range(205):
        member_user = await _mk_user(db)
        db.add(
            OrgMember(
                org_id=org.id,
                user_id=member_user.id,
                role=OrgRole.STUDENT,
                status=MemberStatus.ACTIVE,
            )
        )
    await db.flush()
    invoice = await _force_close(db, sub)
    assert invoice is not None
    lines = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    seat_lines = [line for line in lines if line.line_type == "seats"]
    assert seat_lines == [], (
        f"archived-org students billed as seats: {[(sl.description, sl.amount_minor) for sl in seat_lines]}"
    )


# ── R80: cross-cutting races ─────────────────────────────────


@pytest.mark.asyncio
async def test_checkout_completion_honors_pinned_version(db):
    """R80[2]: the completion webhook re-resolved the CURRENT active plan
    version — racing a version activation bound the paid customer to a
    version/price they never saw. The checkout pins the version and the
    completion honors the pin."""
    from app.controlplane.models.plan import PlanVersion, ProductPlan
    from app.controlplane.services import plans as plan_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    # Resolve the CURRENT active school version (what the customer saw)
    seen_version = (
        await db.execute(
            select(PlanVersion)
            .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
            .where(ProductPlan.key == "school", PlanVersion.status == "active")
        )
    ).scalar_one()
    seen_version_id = seen_version.id
    plan_id = seen_version.plan_id
    # Ops activates a NEW version while the payment settles
    plan = await db.get(ProductPlan, plan_id)
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    new_version = await plan_svc.activate_version(db, draft, actor=_actor(user))
    assert new_version.id != seen_version_id
    try:
        # Webhook completion with the pin → binds the SEEN version
        sub = await billing_svc.activate_subscription_from_checkout(
            db,
            tenant,
            plan_key="school",
            interval="month",
            seats=0,
            provider="mock",
            external_customer_ref="mock_cus_pin",
            external_ref=f"mock_sub_pin_{tenant.id}",
            pinned_version_id=seen_version_id,
        )
        assert sub.plan_version_id == seen_version_id, (
            "customer must get the version they paid for, not the newly activated one"
        )
    finally:
        # restore original active version for other tests
        await db.rollback()


@pytest.mark.asyncio
async def test_refund_returns_money_for_all_payment_methods(db):
    """R80[3]: refund_purchase returned money ONLY for credit-paid purchases —
    checkout (real charge) and invoiced purchases were refunded in name only
    (license revoked, money kept). Non-credit payments now come back as
    platform credit."""
    from app.controlplane.models.credit import CreditLedgerEntry
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase
    from app.controlplane.services import marketplace as market_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    listing = MarketplaceListing(
        product_type="skill_pack",
        product_id=str(ULID()),
        seller_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        seller_tenant_id=tenant.id,
        offer_type="paid",
        price_minor=9900,
        currency="USD",
        license_scope="organization",
        platform_commission_pct=30,
        status="active",
        created_by=user.id,
    )
    db.add(listing)
    await db.flush()
    purchase = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=tenant.id,
        buyer_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        purchaser_user_id=user.id,
        status="paid",
        amount_minor=9900,
        currency="USD",
        economics_snapshot={},
        payment_method="checkout",
        payment_ref="pi_fake",
    )
    db.add(purchase)
    await db.flush()
    await market_svc.refund_purchase(db, purchase.id, reason="defective", actor=_actor(user))
    entry = (
        await db.execute(
            select(CreditLedgerEntry).where(
                CreditLedgerEntry.reference_type == "purchase",
                CreditLedgerEntry.reference_id == purchase.id,
                CreditLedgerEntry.entry_type == "refund",
            )
        )
    ).scalar_one_or_none()
    assert entry is not None, "checkout-paid refund must credit the buyer"
    assert entry.amount_minor == 9900

    # Un-invoiced bill_via_invoice purchase: nothing was charged → no credit
    purchase2 = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=tenant.id,
        buyer_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        purchaser_user_id=user.id,
        status="paid",
        amount_minor=5000,
        currency="USD",
        economics_snapshot={},
        payment_method="invoice",
        invoice_id=None,
    )
    db.add(purchase2)
    await db.flush()
    await market_svc.refund_purchase(db, purchase2.id, reason="cancel", actor=_actor(user))
    entry2 = (
        await db.execute(
            select(CreditLedgerEntry).where(
                CreditLedgerEntry.reference_id == purchase2.id,
                CreditLedgerEntry.entry_type == "refund",
            )
        )
    ).scalar_one_or_none()
    assert entry2 is None, "uncharged invoice purchase must not mint credit"


@pytest.mark.asyncio
async def test_settle_vs_period_close_never_double_charges():
    """R80[1]: handle_run_terminal's rated-row select was unlocked — racing
    close_period_and_invoice, the same rated usage was debited from credit
    AND billed on the invoice. Both sides now take FOR UPDATE on the rows;
    whoever wins excludes the rows from the loser (status flip re-evaluated
    under the lock). Deterministic: close holds its lock while settle runs."""
    import asyncio as _asyncio

    from app.controlplane.models.credit import CreditLedgerEntry, CreditReservation
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.services import credits as credit_svc
    from app.controlplane.services.settlement_handlers import handle_run_terminal
    from app.core.database import AsyncSessionLocal, engine

    try:
        run_id = str(ULID())
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user, status=TenantStatus.ACTIVE)
            await credit_svc.top_up(
                setup,
                tenant.id,
                "USD",
                100_000,
                actor=_actor(user),
                idempotency_key=f"r80-{ULID()}",
            )
            sub, _ = await billing_svc.start_subscription(
                setup,
                tenant,
                plan_key="school",
                interval="month",
                seats=0,
                provider="manual",
                actor=_actor(user),
            )
            # One rated row tied to the run, in-period
            from app.controlplane.services import metering

            event = await metering.emit_usage(
                setup,
                tenant_id=tenant.id,
                org_id="01JFAKEORGFAKEORGFAKEORGFA",
                usage_type="image_generation",
                quantity=1,
                occurred_at=datetime.now(UTC),
                source="workflow_runtime",
                workflow_run_id=run_id,
                idempotency_key=f"r80evt-{ULID()}",
            )
            setup.add(
                RatedUsage(
                    usage_event_id=event.id,
                    tenant_id=tenant.id,
                    org_id="01JFAKEORGFAKEORGFAKEORGFA",
                    usage_type="image_generation",
                    quantity=1,
                    cost_rate_snapshot={},
                    internal_cost_minor=0,
                    internal_cost_currency="USD",
                    sell_rate_snapshot={},
                    billable_amount_minor=500,
                    billable_amount_exact=500,
                    internal_cost_exact=0,
                    billable_currency="USD",
                    status="rated",
                )
            )
            await setup.flush()
            await credit_svc.reserve(
                setup,
                tenant.id,
                "USD",
                500,
                reference_type="workflow_run",
                reference_id=run_id,
            )
            await setup.commit()
            tenant_id, sub_id = tenant.id, sub.id

        # Session A: close the period and HOLD the row lock (no commit yet)
        async with AsyncSessionLocal() as a:
            period = (
                await a.execute(
                    select(BillingPeriod).where(
                        BillingPeriod.subscription_id == sub_id,
                        BillingPeriod.status == "open",
                    )
                )
            ).scalar_one()
            invoice = await billing_svc.close_period_and_invoice(a, period.id)
            assert invoice is not None

            # B: settle concurrently — must BLOCK on the row lock, then see
            # the rows as invoiced (excluded), settling 0.
            async def settle():
                async with AsyncSessionLocal() as b:
                    await handle_run_terminal(b, {"run_id": run_id, "status": "completed"})
                    await b.commit()

            task = _asyncio.create_task(settle())
            await _asyncio.sleep(0.3)
            await a.commit()
            await _asyncio.wait_for(task, timeout=15)

        async with AsyncSessionLocal() as check:
            # The reservation settled at 0 (released the hold, charged nothing)
            reservation = (
                await check.execute(
                    select(CreditReservation).where(
                        CreditReservation.reference_type == "workflow_run",
                        CreditReservation.reference_id == run_id,
                    )
                )
            ).scalar_one()
            assert reservation.status == "settled"
            # The rows were invoiced by the close — the settle must have
            # charged NOTHING against the reservation (0-settle releases the
            # hold). settled_amount is the exact double-charge detector: any
            # positive value here is the same usage charged twice (the
            # invoice's own credit application is a separate, legitimate
            # ledger entry).
            assert (reservation.settled_amount_minor or 0) == 0, (
                "usage charged on the invoice AND from the reservation"
            )
            debits = (
                (
                    await check.execute(
                        select(CreditLedgerEntry).where(
                            CreditLedgerEntry.tenant_id == tenant_id,
                            CreditLedgerEntry.entry_type == "reservation_settle",
                            CreditLedgerEntry.reference_id == run_id,
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert sum(-e.amount_minor for e in debits) == 0, (
                "reservation-side debit landed despite invoice billing"
            )
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_cancel_racing_period_close_no_extra_period():
    """R80[4]: close read sub.status unlocked — a cancel(at_period_end)
    landing mid-close was rolled into a NEW open period (extra full period
    billed). The close now locks the subscription; the racing cancel waits
    and the rollover branch sees the fresh status.

    Serialization test (cancel must WAIT on the close's sub lock and land on
    post-rollover state: one open period, cancel_at_period_end). The exact
    stale-read window is INSIDE close_period_and_invoice and not reachable
    without mid-function hooks, so this is not revert-provable — the FOR
    UPDATE + populate_existing pattern is the same one revert-proven in
    R73[8] (adjust_statement) and R80[1] (settlement select)."""
    import asyncio as _asyncio

    from app.core.database import AsyncSessionLocal, engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user, status=TenantStatus.ACTIVE)
            sub, _ = await billing_svc.start_subscription(
                setup,
                tenant,
                plan_key="school",
                interval="month",
                seats=0,
                provider="manual",
                actor=_actor(user),
            )
            await setup.commit()
            tenant_id, sub_id, user_id = tenant.id, sub.id, user.id

        async with AsyncSessionLocal() as a:
            period = (
                await a.execute(
                    select(BillingPeriod).where(
                        BillingPeriod.subscription_id == sub_id,
                        BillingPeriod.status == "open",
                    )
                )
            ).scalar_one()
            # A holds the close (sub row locked) while B cancels
            invoice = await billing_svc.close_period_and_invoice(a, period.id)
            assert invoice is not None

            async def cancel():
                async with AsyncSessionLocal() as b:
                    t = await b.get(TenantAccount, tenant_id)
                    s = await b.get(Subscription, sub_id)
                    u = await b.get(User, user_id)
                    await billing_svc.cancel_subscription(
                        b, t, s, at_period_end=True, actor=_actor(u)
                    )
                    await b.commit()

            task = _asyncio.create_task(cancel())
            await _asyncio.sleep(0.3)
            await a.commit()
            await _asyncio.wait_for(task, timeout=15)

        async with AsyncSessionLocal() as check:
            fresh = await check.get(Subscription, sub_id)
            open_periods = (
                (
                    await check.execute(
                        select(BillingPeriod).where(
                            BillingPeriod.subscription_id == sub_id,
                            BillingPeriod.status == "open",
                        )
                    )
                )
                .scalars()
                .all()
            )
            # The close rolled a new period BEFORE the cancel landed — that's
            # the correct serialization (cancel waited). The cancel then
            # flagged at_period_end on the NEW period: exactly one open
            # period, sub in cancel_at_period_end.
            assert fresh.status == "cancel_at_period_end"
            assert len(open_periods) == 1
    finally:
        await engine.dispose()


# ── R81/R82: stripe currency case + proration gap/truncation + void rewind ──


def test_minor_multiplier_case_insensitive():
    """R81[0]: Stripe webhooks send LOWERCASE currency ('jpy'); a raw dict
    miss fell through to ×100, over-crediting JPY/KRW top-ups 100x."""
    from app.controlplane.models.pricing import minor_multiplier
    from app.controlplane.services.billing_providers.stripe import (
        _platform_minor_from_stripe,
    )

    assert minor_multiplier("jpy") == 1
    assert minor_multiplier("JPY") == 1
    assert minor_multiplier("krw") == 1
    assert minor_multiplier("usd") == 100
    # end-to-end: ¥1000 webhook → 1000 platform minor, not 100000
    assert _platform_minor_from_stripe(1000, "jpy") == 1000
    assert _platform_minor_from_stripe(50000, "krw") == 50000
    assert _platform_minor_from_stripe(1000, "usd") == 1000  # $10.00 both sides


def test_zero_decimal_currency_set_frozen_r300():
    """R300: the zero-decimal currency set is maintained INDEPENDENTLY in two
    languages — CURRENCY_MINOR here and ZERO_DECIMAL in apps/web/src/lib/cp.ts.
    A drift (backend treats a currency as zero-decimal, frontend still ÷100 or
    vice-versa) is a 100x money-DISPLAY error — the exact R81/R163 class that
    has already recurred twice. This pins the backend side to {JPY, KRW}; the
    reciprocal frontend test (cp-money.test.ts) pins the same. Adding a v1
    currency fires BOTH, forcing the two sides to be updated together."""
    from app.controlplane.models.pricing import CURRENCY_MINOR, DEFAULT_MINOR

    zero_decimal = {c for c, m in CURRENCY_MINOR.items() if m == 1}
    assert zero_decimal == {"JPY", "KRW"}, (
        "backend zero-decimal set changed — update apps/web/src/lib/cp.ts "
        "ZERO_DECIMAL to match, then this assertion"
    )
    assert DEFAULT_MINOR == 100
    # every declared multiplier is either zero-decimal (1) or 2-decimal (100)
    assert set(CURRENCY_MINOR.values()) <= {1, 100}


@pytest.mark.asyncio
async def test_gap_change_bills_ended_period_at_old_plan(db):
    """R82[1]: an immediate change landing AFTER period_end but BEFORE the
    hourly close billed the entire just-ended period at the NEW plan. The
    first_change query must have no upper bound — the earliest immediate
    change since period_start carries the true period-start plan."""
    from datetime import timedelta as _td

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    # End the period in the past (simulates the cron gap: period over,
    # close not yet run)
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    from app.controlplane.services.billing import _add_interval

    # Anchor an exact natural month fully in the past (truncation proration
    # ratio == 1), leaving a gap between period_end and "now" for the change.
    period.period_start = datetime.now(UTC) - _td(days=40)
    period.period_end = _add_interval(period.period_start, "month")
    sub.current_period_end = period.period_end
    sub.current_period_start = period.period_start
    await db.flush()
    # Gap change: immediate upgrade school -> growth NOW (after period_end)
    await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key="growth",
        seats=None,
        proration_mode="immediate",
        actor=_actor(user),
    )
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None
    lines = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    plan_lines = [line for line in lines if line.line_type == "plan"]
    assert len(plan_lines) == 1
    # school monthly = 19900; growth = 49900. The ended period must bill school.
    assert plan_lines[0].amount_minor == 19900, (
        f"gap change billed the ended period at the NEW plan: {plan_lines[0].amount_minor}"
    )


@pytest.mark.asyncio
async def test_immediate_cancel_prorates_final_partial_period(db):
    """R82[2]: an immediate cancel truncates the period to now, but the plan
    line charged the FULL interval fee. The final partial period must be
    prorated by actual/natural length."""
    from datetime import timedelta as _td

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    # Simulate: subscribed 10 days ago, cancel now (period truncated to now)
    period.period_start = datetime.now(UTC) - _td(days=10)
    sub.current_period_start = period.period_start
    await db.flush()
    sub = await billing_svc.cancel_subscription(
        db, tenant, sub, at_period_end=False, actor=_actor(user)
    )
    await db.refresh(period)
    assert period.period_end <= datetime.now(UTC) + _td(seconds=5)
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None
    lines = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    plan_lines = [line for line in lines if line.line_type == "plan"]
    assert len(plan_lines) == 1
    # ~10 of ~30-31 days: roughly a third of 19900, definitely NOT the full fee
    assert plan_lines[0].amount_minor < 19900, "full fee charged for a truncated period"
    assert 4000 < plan_lines[0].amount_minor < 8000, plan_lines[0].amount_minor


@pytest.mark.asyncio
async def test_void_older_invoice_does_not_rewind_later_periods(db):
    """R82[3]: voiding an OLDER open invoice deleted already-INVOICED (even
    paid) forward periods and re-billed them. Rewind only fires when no
    later non-open period exists."""
    from datetime import timedelta as _td

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    # Close period 1 → invoice A (open), sub rolls to period 2
    p1 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    p1.period_end = datetime.now(UTC) - _td(days=31)
    p1.period_start = p1.period_end - _td(days=30)
    await db.flush()
    inv_a = await billing_svc.close_period_and_invoice(db, p1.id)
    assert inv_a is not None
    # Close period 2 → invoice B, sub rolls to period 3
    p2 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    p2.period_end = datetime.now(UTC) - _td(days=1)
    await db.flush()
    inv_b = await billing_svc.close_period_and_invoice(db, p2.id)
    assert inv_b is not None
    p2_id = p2.id
    # Void the OLDER invoice A — p2 (invoiced) must survive, no rewind
    await billing_svc.void_invoice(db, inv_a, reason="disputed", actor=_actor(user))
    p2_after = await db.get(BillingPeriod, p2_id)
    assert p2_after is not None, "void of older invoice deleted a later invoiced period"
    assert p2_after.status == "invoiced"
    # Sub window not rolled back to p1
    await db.refresh(sub)
    assert sub.current_period_start >= p2_after.period_end


@pytest.mark.asyncio
async def test_credit_note_on_open_invoice_refunds_collected_portion(db):
    """R88[10]: on an open invoice, a note larger than amount_due covers
    money already COLLECTED (credit applied at close / partial payments) —
    flooring at 0 silently kept it. The excess must come back as a ledger
    refund."""
    from datetime import timedelta as _td

    from app.controlplane.models.credit import CreditLedgerEntry
    from app.controlplane.services import credits as credit_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    # Give credit so the close applies it (collected money on the invoice)
    await credit_svc.top_up(
        db, tenant.id, "USD", 5000, actor=_actor(user), idempotency_key=f"cn88-{ULID()}"
    )
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    from app.controlplane.services.billing import _add_interval

    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    period.period_start = datetime.now(UTC) - _td(days=40)
    period.period_end = _add_interval(period.period_start, "month")
    sub.current_period_start = period.period_start
    sub.current_period_end = period.period_end
    await db.flush()
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None
    await db.refresh(invoice)
    # total 19900, credit applied 5000 → due 14900, still open
    assert invoice.status == "open"
    assert invoice.credit_applied_minor == 5000
    assert invoice.amount_due_minor == 14900
    # Full credit note 19900: 14900 kills the debt, 5000 (collected) refunds
    note = await billing_svc.issue_credit_note(
        db, invoice, amount_minor=19900, reason="full refund", actor=_actor(user)
    )
    await db.refresh(invoice)
    assert invoice.amount_due_minor == 0
    refund = (
        await db.execute(
            select(CreditLedgerEntry).where(
                CreditLedgerEntry.reference_type == "credit_note",
                CreditLedgerEntry.reference_id == note.id,
            )
        )
    ).scalar_one_or_none()
    assert refund is not None, "collected portion must come back as credit"
    assert refund.amount_minor == 5000


@pytest.mark.asyncio
async def test_refund_invoiced_purchase_only_when_collected(db):
    """R88[11]: refunding a purchase whose license line sits on a still-OPEN
    invoice minted credit for money never received. Refund mints only when
    the invoice actually collected (paid)."""
    from app.controlplane.models.credit import CreditLedgerEntry
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase
    from app.controlplane.services import marketplace as market_svc

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    listing = MarketplaceListing(
        product_type="skill_pack",
        product_id=str(ULID()),
        seller_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        seller_tenant_id=tenant.id,
        offer_type="paid",
        price_minor=5000,
        currency="USD",
        license_scope="organization",
        platform_commission_pct=30,
        status="active",
        created_by=user.id,
        bill_via_invoice=True,
    )
    db.add(listing)
    await db.flush()
    # invoiced on an OPEN invoice
    inv = Invoice(tenant_id=tenant.id, status="open", currency="USD", total_minor=5000)
    db.add(inv)
    await db.flush()
    purchase = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=tenant.id,
        buyer_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        purchaser_user_id=user.id,
        status="paid",
        amount_minor=5000,
        currency="USD",
        economics_snapshot={},
        payment_method="invoice",
        invoice_id=inv.id,
    )
    db.add(purchase)
    await db.flush()
    await market_svc.refund_purchase(db, purchase.id, reason="open-inv", actor=_actor(user))
    minted = (
        await db.execute(
            select(CreditLedgerEntry).where(
                CreditLedgerEntry.reference_id == purchase.id,
                CreditLedgerEntry.entry_type == "refund",
            )
        )
    ).scalar_one_or_none()
    assert minted is None, "refund minted credit for uncollected invoice money"
    # PAID invoice → refund mints
    inv2 = Invoice(tenant_id=tenant.id, status="paid", currency="USD", total_minor=5000)
    db.add(inv2)
    await db.flush()
    purchase2 = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=tenant.id,
        buyer_org_id="01JFAKEORGFAKEORGFAKEORGFA",
        purchaser_user_id=user.id,
        status="paid",
        amount_minor=5000,
        currency="USD",
        economics_snapshot={},
        payment_method="invoice",
        invoice_id=inv2.id,
    )
    db.add(purchase2)
    await db.flush()
    await market_svc.refund_purchase(db, purchase2.id, reason="paid-inv", actor=_actor(user))
    minted2 = (
        await db.execute(
            select(CreditLedgerEntry).where(
                CreditLedgerEntry.reference_id == purchase2.id,
                CreditLedgerEntry.entry_type == "refund",
            )
        )
    ).scalar_one_or_none()
    assert minted2 is not None and minted2.amount_minor == 5000


def test_stripe_sdk_calls_offloaded_to_thread(monkeypatch):
    """R89[13]: the sync stripe SDK was called inline in async methods —
    every Stripe HTTP round-trip froze the whole event loop. Each SDK call
    must run OFF the event-loop thread (asyncio.to_thread)."""
    import asyncio as _asyncio
    import threading
    import types

    from app.config import settings as app_settings
    from app.controlplane.services.billing_providers.stripe import StripeProvider

    monkeypatch.setattr(app_settings, "stripe_secret_key", "sk_test_x")
    call_threads: dict = {}

    def cap(name, ret):
        def f(*a, **kw):
            call_threads[name] = threading.current_thread()
            return ret

        return f

    fake = types.ModuleType("stripe")
    fake.api_key = None
    fake.Customer = types.SimpleNamespace(create=cap("customer", {"id": "cus_1"}))
    fake.checkout = types.SimpleNamespace(
        Session=types.SimpleNamespace(
            create=cap("checkout", {"id": "cs_1", "url": "https://pay"}),
            retrieve=cap("session", {"payment_status": "paid"}),
        )
    )
    fake.Subscription = types.SimpleNamespace(
        retrieve=cap("sub_get", {"items": {"data": [{"id": "si_1"}]}}),
        modify=cap("sub_mod", {"id": "sub_1"}),
        cancel=cap("sub_cancel", {"id": "sub_1"}),
    )
    monkeypatch.setitem(__import__("sys").modules, "stripe", fake)

    p = StripeProvider()
    tenant = types.SimpleNamespace(id="01TENANT", name="Acme", billing_email="a@b.c")

    async def run():
        main_thread = threading.current_thread()
        await p.create_customer(tenant)
        await p.change_subscription("sub_1", "price_x", 3)
        await p.cancel_subscription("sub_1", at_period_end=True)
        await p.fetch_payment_status("cs_1")
        for name, t in call_threads.items():
            assert t is not main_thread, f"SDK call '{name}' ran ON the event loop thread"

    _asyncio.run(run())


@pytest.mark.asyncio
async def test_mock_subscription_blocked_in_production(db, monkeypatch):
    """R113[A0]: a mock-provider subscription in production gives the customer
    a dead mock-checkout URL and a subscription that never collects money —
    same class as marketplace checkout's R64[18] guard. The endpoint resolves
    mock → stripe when configured, else 409s in production."""
    from fastapi import Request as _Req

    from app.config import settings as app_settings
    from app.controlplane.api import billing as billing_api
    from app.controlplane.api.billing import StartSubscriptionRequest
    from app.exceptions import AppError

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.TRIAL)

    monkeypatch.setattr(app_settings, "app_env", "production")
    monkeypatch.setattr(app_settings, "stripe_secret_key", "")
    scope = {"type": "http", "method": "POST", "path": "/", "headers": [], "query_string": b""}
    with pytest.raises(AppError) as exc:
        await billing_api.start_subscription(
            tenant.id,
            StartSubscriptionRequest(plan_key="school", interval="month", provider="mock"),
            _Req(scope),
            user=user,
            db=db,
        )
    assert exc.value.code == "BILLING_PROVIDER_UNCONFIGURED"
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_seat_increase_then_decrease_bills_per_segment(db):
    """R113[H7] (R101[H22] regression): an increase-then-decrease within one
    period must bill the raised floor only for ITS OWN segment. The per-change
    walk charged the increase's full delta over ALL remaining days (past the
    later decrease) on top of the base line — a real-money over-charge."""
    from datetime import timedelta

    from app.controlplane.models.billing import SubscriptionChange

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    # school: included_seats=200, overage $5.00/seat (seed)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=205, provider="manual", actor=a
    )
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    total_days = max((period.period_end - period.period_start).days, 1)
    d10 = period.period_start + timedelta(days=10)
    d20 = period.period_start + timedelta(days=20)
    # Two immediate seat changes recorded directly (bypasses live-seat quota):
    # 205 → 220 at day 10, 220 → 208 at day 20.
    for eff, frm, to in ((d10, 205, 220), (d20, 220, 208)):
        db.add(
            SubscriptionChange(
                subscription_id=sub.id,
                change_type="seat_change",
                from_plan_version_id=sub.plan_version_id,
                to_plan_version_id=sub.plan_version_id,
                from_seats=frm,
                to_seats=to,
                effective_at=eff,
                proration_mode="immediate",
                created_by=user.id,
            )
        )
    sub.seat_quantity = 208
    await db.flush()
    inv = await billing_svc.close_period_and_invoice(db, period.id)
    lines = await _lines(db, inv)
    seats_total = _plan_lines_total(lines, "seats")
    proration_total = _plan_lines_total(lines, "proration")
    # Base seats line: max(live=0, start=205) − included 200 = 5 seats × $5.
    assert seats_total == 5 * 500, seats_total
    # Segment extras: [d10,d20) floor 220 → 15 over the billed 205 for 10 of
    # total_days; [d20,end) floor 208 → 3 extra seats for the remaining days.
    seg2_days = total_days - 20
    expected = round(15 * 500 * 10 / total_days) + round(3 * 500 * seg2_days / total_days)
    assert abs(proration_total - expected) <= 2, (proration_total, expected)
    # The pre-fix walk billed the day-10 delta over ALL 20 remaining days
    # (~15×500×20/30 = 5000 alone) — assert we are well under that.
    assert proration_total < 5000, proration_total


@pytest.mark.asyncio
async def test_plan_change_reprices_seat_band_per_segment(db):
    """R123[C0]: a mid-period plan change that RAISES included_seats must stop
    charging the base-line overage for the post-change segment. The H7
    floor-only extra billed the old plan's full-period overage regardless —
    over-charging the exact upgrade that bought more included seats."""
    from datetime import timedelta

    from app.controlplane.models.billing import SubscriptionChange
    from app.controlplane.models.plan import PlanPrice, PlanVersion, ProductPlan

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    # school: included 200, $5 overage. growth: included 1000 (covers overage).
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=215, provider="manual", actor=a
    )
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    total_days = max((period.period_end - period.period_start).days, 1)
    growth_version_id = (
        await db.execute(
            select(PlanVersion.id)
            .join(ProductPlan, ProductPlan.id == PlanVersion.plan_id)
            .where(ProductPlan.key == "growth", PlanVersion.status == "active")
        )
    ).scalar_one()
    mid = period.period_start + timedelta(days=total_days // 2)
    db.add(
        SubscriptionChange(
            subscription_id=sub.id,
            change_type="plan_change",
            from_plan_version_id=sub.plan_version_id,
            to_plan_version_id=growth_version_id,
            from_seats=215,
            to_seats=215,
            effective_at=mid,
            proration_mode="immediate",
            created_by=user.id,
        )
    )
    sub.plan_version_id = growth_version_id
    await db.flush()
    inv = await billing_svc.close_period_and_invoice(db, period.id)
    lines = await _lines(db, inv)
    seats_total = _plan_lines_total(lines, "seats")
    # Base line: 15 over school's 200 included × $5 = 7500 (full period)
    assert seats_total == 15 * 500, seats_total
    # The proration line must CREDIT the post-change half of that overage
    # (growth includes 1000 seats → zero overage after the change), on top of
    # the plan-fee delta.
    growth_price = (
        await db.execute(
            select(PlanPrice).where(
                PlanPrice.plan_version_id == growth_version_id,
                PlanPrice.currency == "USD",
                PlanPrice.interval == "month",
            )
        )
    ).scalar_one()
    school_price_minor = 19900
    seg_days = total_days - (total_days // 2)
    expected_fee_delta = round(
        (growth_price.amount_minor - school_price_minor) * seg_days / total_days
    )
    expected_seat_credit = -round(15 * 500 * seg_days / total_days)
    proration_total = _plan_lines_total(lines, "proration")
    assert abs(proration_total - (expected_fee_delta + expected_seat_credit)) <= 2, (
        proration_total,
        expected_fee_delta,
        expected_seat_credit,
    )


# ── R129 batch regressions ───────────────────────────────────


def test_preview_band_repricing_matches_close_walk():
    """R129[M5]: the preview's seat component must mirror the close's
    R123[C0] band repricing — a plan change that shrinks included_seats
    CHARGES the newly exposed band even when the reserved floor is unchanged.
    Plan A: fee 10000, included 10, seat 500; live 10 seats. Change to plan
    B: fee 8000, included 2, seat 500, floor unchanged at day 15/30. Legacy
    delta math showed -1000 (credit); the invoice charges +1000."""
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = datetime(2026, 10, 1, tzinfo=UTC)
    at = datetime(2026, 9, 16, tzinfo=UTC)  # 15 days left
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=10000,
        new_amount_minor=8000,
        old_seats=10,
        new_seats=10,
        seat_price_minor=500,
        billable_seats=10,
        old_included_seats=10,
        new_included_seats=2,
        old_seat_price_minor=500,
    )
    # fee delta (8000-10000)×15/30 = -1000; band delta (8×500 - 0)×15/30 = +2000
    assert p["seat_proration_minor"] == 2000
    assert p["net_minor"] == 1000
    # And the reverse (band widens) shows the credit the invoice grants.
    p2 = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=8000,
        new_amount_minor=10000,
        old_seats=10,
        new_seats=10,
        seat_price_minor=500,
        billable_seats=10,
        old_included_seats=2,
        new_included_seats=10,
        old_seat_price_minor=500,
    )
    assert p2["seat_proration_minor"] == -2000
    # Legacy path (no billable_seats) still uses the floor-delta math.
    p3 = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=0,
        new_amount_minor=0,
        old_seats=10,
        new_seats=20,
        seat_price_minor=500,
    )
    assert p3["seat_proration_minor"] == 2500


@pytest.mark.asyncio
async def test_void_after_cancel_close_recancels_not_rebills(db):
    """R129[C1] → R130 rework: voiding the FINAL invoice of a cancelled sub
    must leave it CANCELLED (the terminal-close branch bills a cancelled
    sub's period without rolling forward) and enqueue the re-close directly
    — the R129 resurrect-to-cancel_at_period_end was escapable via
    reactivate_subscription and violated uq_cp_sub_live once the tenant had
    re-subscribed. The original bug (restore-to-'active' → rollover →
    perpetual re-bill) must stay fixed."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=True, actor=a)
    inv = await _force_close(db, sub)
    assert inv is not None
    await db.refresh(sub)
    assert sub.status == "cancelled"
    period_id = inv.billing_period_id

    await billing_svc.void_invoice(db, inv, reason="final invoice dispute", actor=a)
    await db.refresh(sub)
    # Stays cancelled — no resurrect (reactivate must NOT become possible,
    # and a successor subscription must not violate uq_cp_sub_live).
    assert sub.status == "cancelled"
    # The re-close is enqueued directly (scan_due_periods skips cancelled).
    msgs = (
        (await db.execute(select(OutboxMessage).where(OutboxMessage.topic == "period.close_due")))
        .scalars()
        .all()
    )
    assert any(m.payload.get("billing_period_id") == period_id for m in msgs), (
        "void of a terminal-close invoice must enqueue the re-close itself"
    )

    inv2 = await billing_svc.close_period_and_invoice(db, period_id)
    assert inv2 is not None and inv2.id != inv.id
    # Re-close terminates — still cancelled, NO new open period.
    await db.refresh(sub)
    assert sub.status == "cancelled"
    open_periods = (
        await db.execute(
            select(func.count(BillingPeriod.id)).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    assert open_periods == 0
    # And the regenerated invoice bills the same period's plan fee once.
    assert _plan_lines_total(await _lines(db, inv2), "plan") == 19900
    # A successor subscription is startable after the void (no unique-index
    # violation from any resurrect) — the R130 [0] shape.
    sub2, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    assert sub2.id != sub.id


@pytest.mark.asyncio
async def test_void_older_invoice_no_rewind_when_cancel_scheduled_later(db):
    """R130[4]/[23]: voiding period N's invoice while a cancellation is
    scheduled in the OPEN period N+1 must NOT rewind — the rewind deleted
    N+1 and the re-close's terminal branch cancelled one period early,
    silently discarding N+1's plan fee and remaining paid access."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    inv_n = await _force_close(db, sub)  # closes N, rolls to N+1 (open)
    assert inv_n is not None
    # Tenant schedules cancel-at-period-end during N+1.
    await db.refresh(sub)
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=True, actor=a)
    await db.refresh(sub)
    assert sub.status == "cancel_at_period_end"
    n1 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()

    # Void N's invoice — must void PLAINLY (no rewind, no N+1 delete).
    await billing_svc.void_invoice(db, inv_n, reason="june dispute", actor=a)
    await db.refresh(sub)
    assert sub.status == "cancel_at_period_end", "void must not touch the scheduled cancel"
    still_open = await db.get(BillingPeriod, n1.id)
    assert still_open is not None and still_open.status == "open", (
        "the later open period must survive the void"
    )
    voided_period = await db.get(BillingPeriod, inv_n.billing_period_id)
    assert voided_period.status == "invoiced", "no rewind: the voided period stays invoiced"


def test_preview_seat_days_match_close_segment_days():
    """R130[3]: the preview's seat component must count days the way the
    close's segment walk does — floor(period_end − at), not
    total − floor(at − start), which is one day larger for any
    non-midnight change."""
    start = datetime(2026, 9, 1, tzinfo=UTC)
    end = datetime(2026, 10, 1, tzinfo=UTC)
    at = datetime(2026, 9, 16, 12, 0, tzinfo=UTC)  # midday: 14.5 days remain
    p = billing_svc.proration_preview(
        period_start=start,
        period_end=end,
        at=at,
        old_amount_minor=0,
        new_amount_minor=0,
        old_seats=0,
        new_seats=8,
        seat_price_minor=500,
        billable_seats=0,
        old_included_seats=0,
        new_included_seats=0,
        old_seat_price_minor=500,
    )
    # close: seg_days = floor(14.5) = 14 → 8×500×14/30 = 1867
    assert p["seat_proration_minor"] == 1867


@pytest.mark.asyncio
async def test_void_rewind_enqueues_immediate_reclose(db):
    """R131 ([0]): every rewind enqueues the re-close directly — waiting for
    the hourly cron left a ≤1h window where a tenant cancel-at-period-end
    turned the re-close terminal one period early."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    inv = await _force_close(db, sub)  # rollover close (sub stays active)
    assert inv is not None
    period_id = inv.billing_period_id
    await billing_svc.void_invoice(db, inv, reason="dispute", actor=a)
    msgs = (
        (await db.execute(select(OutboxMessage).where(OutboxMessage.topic == "period.close_due")))
        .scalars()
        .all()
    )
    assert any(m.payload.get("billing_period_id") == period_id for m in msgs), (
        "void rewind of an ACTIVE sub must enqueue the re-close immediately"
    )


@pytest.mark.asyncio
async def test_cancelled_sub_blocked_reclose_reenqueues(db):
    """R131 ([1]): a cancelled sub's re-close bouncing on blocked ratings must
    re-enqueue itself (delayed) — the single void-enqueued message was the
    only shot and 'done' stranded the final invoice forever."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=False, actor=a)
    await db.refresh(sub)
    assert sub.status == "cancelled"
    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    # Plant a BLOCKED rated row for the tenant → the close must abort+reopen.
    ev = UsageEvent(
        tenant_id=tenant.id,
        org_id="01JBLORGY00000000000000000",
        usage_type="image_generation",
        quantity=1,
        unit="images",
        occurred_at=datetime.now(UTC),
        source="manual",
    )
    db.add(ev)
    await db.flush()
    db.add(
        RatedUsage(
            usage_event_id=ev.id,
            tenant_id=tenant.id,
            org_id=ev.org_id,
            usage_type=ev.usage_type,
            quantity=ev.quantity,
            cost_rate_snapshot={},
            internal_cost_minor=0,
            internal_cost_currency="USD",
            sell_rate_snapshot={"fx_gaps": ["ZZZ->USD"]},
            billable_amount_minor=0,
            billable_currency="USD",
            status="blocked",
        )
    )
    await db.flush()
    inv = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv is None, "blocked ratings must abort the close"
    await db.refresh(period)
    assert period.status == "open"
    retry = (
        (await db.execute(select(OutboxMessage).where(OutboxMessage.topic == "period.close_due")))
        .scalars()
        .all()
    )
    mine = [m for m in retry if m.payload.get("billing_period_id") == period.id]
    assert mine, "cancelled-sub blocked abort must re-enqueue its own retry"
    assert any(m.available_at > datetime.now(UTC) for m in mine), (
        "the retry must be DELAYED (backoff), not immediate"
    )


@pytest.mark.asyncio
async def test_void_restores_rollover_applied_plan(db):
    """R132 ([F16]): voiding a rollover invoice whose close APPLIED a deferred
    (next_period) downgrade must restore the sub's plan/seats to the OLD
    values — otherwise the re-close bills the voided period at the NEW plan
    (arrears falls back to sub.plan_version_id with no immediate change
    anchoring the period start)."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    # DECOY: another tenant's sub with a forward IMMEDIATE change — the
    # restore's forward-ownership discriminator must scope to THIS sub
    # (R350: the flipped sub filter finds the decoy and skips the restore)
    t_d = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub_d, _ = await billing_svc.start_subscription(
        db, t_d, plan_key="school", interval="month", seats=0, provider="manual", actor=a)
    # Deferred downgrade growth → school (next_period) WITH a seats axis
    # (0 → 4): the fold applies BOTH axes; the void must restore BOTH.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=4, proration_mode="next_period", actor=a
    )
    await billing_svc.change_plan(
        db, t_d, sub_d, plan_key="growth", seats=None, proration_mode="immediate", actor=a)
    inv = await _force_close(db, sub)  # rollover: applies the downgrade
    assert inv is not None
    await db.refresh(sub)
    assert sub.seat_quantity == 4                       # seats axis folded
    growth_version = None  # capture post-void expectation via the change row
    from app.controlplane.models.billing import SubscriptionChange

    chg = (
        await db.execute(
            select(SubscriptionChange).where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.change_type == "plan_change",
            )
        )
    ).scalar_one()
    growth_version = chg.from_plan_version_id
    assert sub.plan_version_id == chg.to_plan_version_id  # downgrade applied

    await billing_svc.void_invoice(db, inv, reason="rollover dispute", actor=a)
    await db.refresh(sub)
    assert sub.plan_version_id == growth_version, (
        "void must restore the pre-rollover plan for the arrears re-close"
    )
    assert sub.seat_quantity == 0, "void must restore the pre-rollover seats too"
    # Re-close bills the voided period at the OLD (growth) fee.
    inv2 = await billing_svc.close_period_and_invoice(db, inv.billing_period_id)
    assert inv2 is not None
    assert _plan_lines_total(await _lines(db, inv2), "plan") == 49900, (
        "re-close must bill the voided period at the original plan"
    )
    # And the downgrade is re-applied at the re-rollover.
    await db.refresh(sub)
    assert sub.plan_version_id == chg.to_plan_version_id
    assert sub.seat_quantity == 4

    # R350 (L2003 boundary): the deferred change's effective_at sits EXACTLY
    # at the next period's start — voiding THAT period's invoice must
    # un-invoice it (>=, not >), or the re-close silently drops the change.
    inv3 = await _force_close(db, sub)                  # close period 2
    assert inv3 is not None
    await db.refresh(chg)
    assert chg.invoiced is True
    await billing_svc.void_invoice(db, inv3, reason="p2 dispute", actor=a)
    await db.refresh(chg)
    assert chg.invoiced is False, (
        "a change effective exactly at the period start must be un-invoiced")


@pytest.mark.asyncio
async def test_void_reclose_with_forward_immediate_upgrade(db):
    """R132 ([19]): void-rewind of period 1 while the tenant made an IMMEDIATE
    upgrade in period 2 — the re-close must (a) bill period 1 at its true
    plan (not the forward change's from_*), and (b) NOT clobber the paid
    immediate upgrade when re-folding the re-armed deferred downgrade."""

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    # Backdate the period so the close runs at (past) natural end — the
    # forward-window immediate change must land AFTER period_end, as in
    # production (the hourly close fires once period_end <= now).
    from datetime import timedelta

    p1 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    shift = datetime.now(UTC) - timedelta(seconds=1) - p1.period_end
    p1.period_start = p1.period_start + shift
    p1.period_end = p1.period_end + shift
    sub.current_period_start = p1.period_start
    sub.current_period_end = p1.period_end
    await db.flush()
    # Deferred downgrade growth → school (effective at the past period end).
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=None, proration_mode="next_period", actor=a
    )
    inv1 = await billing_svc.close_period_and_invoice(db, p1.id)
    assert inv1 is not None
    await db.refresh(sub)
    # DECOY sub (another tenant) with its own immediate change in the same
    # window — ownership detection must not read it as THIS sub's forward
    # change (R350)
    t_d2 = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub_d2, _ = await billing_svc.start_subscription(
        db, t_d2, plan_key="school", interval="month", seats=0, provider="manual", actor=a)
    await billing_svc.change_plan(
        db, t_d2, sub_d2, plan_key="growth", seats=None, proration_mode="immediate", actor=a)
    # Tenant IMMEDIATELY upgrades back school → growth inside period 2
    # (effective_at = now > P1.period_end).
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="growth", seats=None, proration_mode="immediate", actor=a
    )
    await db.refresh(sub)
    upgrade_version = sub.plan_version_id  # growth again

    # Ops void period 1's invoice → rewind (P2 open, sub active).
    await billing_svc.void_invoice(db, inv1, reason="p1 dispute", actor=a)
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    # (a) period 1 re-billed at GROWTH (49900, minus seconds-level backdating
    # proration), never at school's 19900.
    plan_total = _plan_lines_total(await _lines(db, inv2), "plan")
    assert plan_total > 45000, (
        f"re-close must bill period 1 at its true (growth) plan, got {plan_total}"
    )
    # (b) the tenant's paid immediate upgrade survives the re-rollover.
    await db.refresh(sub)
    assert sub.plan_version_id == upgrade_version, (
        "re-rollover must not clobber the later immediate upgrade"
    )


@pytest.mark.asyncio
async def test_normal_close_folds_deferred_downgrade_despite_seat_bump(db):
    """R133 ([F3] verified): the fold-supersede must not fire on the NORMAL
    close path nor across axes — a scheduled plan downgrade followed by a
    routine immediate seat bump must still take effect at rollover."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    # Scheduled downgrade growth → school.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=None, proration_mode="next_period", actor=a
    )
    # Routine immediate seat bump AFTER the deferred change.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=5, proration_mode="immediate", actor=a
    )
    from app.controlplane.models.billing import SubscriptionChange

    downgrade = (
        await db.execute(
            select(SubscriptionChange).where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.proration_mode == "next_period",
            )
        )
    ).scalar_one()
    school_version = downgrade.to_plan_version_id

    inv = await _force_close(db, sub)  # normal rollover — no void anywhere
    assert inv is not None
    await db.refresh(sub)
    assert sub.plan_version_id == school_version, (
        "the scheduled downgrade must fold at the normal rollover — a later "
        "immediate seat bump must not suppress it"
    )
    assert sub.seat_quantity == 5, "the seat bump must survive"


@pytest.mark.asyncio
async def test_reclose_reproduces_fold_despite_in_period_immediate_change(db):
    """R134 ([0]): an IMMEDIATE change made in the same period BEFORE the
    original close must not supersede the deferred change on re-close — the
    original rollover folded the deferred change over it, and the re-close
    must reproduce that outcome (close_snapshot watermark divider), not drop
    the scheduled downgrade via global id order."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    # (1) deferred downgrade school → community (next_period)…
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="community", seats=None, proration_mode="next_period", actor=a
    )
    # (2) …then, later the SAME period, an immediate upgrade school → growth.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="growth", seats=None, proration_mode="immediate", actor=a
    )
    from app.controlplane.models.billing import SubscriptionChange

    deferred = (
        await db.execute(
            select(SubscriptionChange).where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.proration_mode == "next_period",
            )
        )
    ).scalar_one()
    # (3) original close: arrears anchored on the immediate change's from_*
    # (school), rollover folds the deferred downgrade → community.
    inv1 = await _force_close(db, sub)
    assert inv1 is not None
    await db.refresh(sub)
    assert sub.plan_version_id == deferred.to_plan_version_id, (
        "normal rollover folds the deferred downgrade (R133 [F3])"
    )
    # (4) void + (5) re-close: the in-period immediate change (id <= the
    # original close's watermark) must NOT supersede the deferred change.
    await billing_svc.void_invoice(db, inv1, reason="dispute", actor=a)
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    await db.refresh(sub)
    assert sub.plan_version_id == deferred.to_plan_version_id, (
        "re-close must reproduce the original fold — the in-period immediate "
        "change was already folded-over by the original close"
    )
    # And the arrears basis matches the original: period billed at school.
    assert _plan_lines_total(await _lines(db, inv1), "plan") == _plan_lines_total(
        await _lines(db, inv2), "plan"
    ), "re-close must bill the same plan fee as the voided original"


@pytest.mark.asyncio
async def test_reclose_bills_snapshot_seats_when_forward_change_owns_axis(db):
    """R134 ([1]): forward-window immediate seat bump + voided period whose
    rollover folded a deferred seat drop — the re-close must bill the voided
    period at its ORIGINAL seat floor (close_snapshot), not the forward
    value that sub.seat_quantity now holds. Community plan: included 25,
    $5 overage — floors must exceed included or the line is vacuously 0."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="community", interval="month", seats=40, provider="manual", actor=a
    )
    p1 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    # Backdate so the forward change lands after period_end (production shape).
    shift = datetime.now(UTC) - timedelta(seconds=1) - p1.period_end
    p1.period_start = p1.period_start + shift
    p1.period_end = p1.period_end + shift
    sub.current_period_start = p1.period_start
    sub.current_period_end = p1.period_end
    await db.flush()
    # Deferred seat drop 40 → 30 (next_period).
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=30, proration_mode="next_period", actor=a
    )
    inv1 = await billing_svc.close_period_and_invoice(db, p1.id)
    assert inv1 is not None
    await db.refresh(sub)
    assert sub.seat_quantity == 30, "rollover folds the deferred seat drop"
    seats1 = _plan_lines_total(await _lines(db, inv1), "seats")
    # (40-25)*500 scaled by the backdated period's truncation ratio (~30/31).
    assert seats1 > 0, "floor 40 over included 25 must produce a seats line"
    # Forward-window immediate seat bump 30 → 300 in period 2.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=300, proration_mode="immediate", actor=a
    )
    await db.refresh(sub)
    assert sub.seat_quantity == 300
    # Void P1 → the seat restore is correctly skipped (forward change owns
    # the axis) — but the re-close must still bill P1 at floor 40.
    await billing_svc.void_invoice(db, inv1, reason="p1 dispute", actor=a)
    await db.refresh(sub)
    assert sub.seat_quantity == 300, "void must not clobber the paid forward seat bump"
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    seats2 = _plan_lines_total(await _lines(db, inv2), "seats")
    assert seats2 == seats1, (
        f"re-close must bill the voided period at its original seat floor "
        f"(got {seats2}, original {seats1})"
    )


@pytest.mark.asyncio
async def test_void_restore_with_stacked_deferred_changes(db):
    """R134 ([15]): TWO stacked next_period changes fold last-wins at the
    rollover; voiding that invoice must rewind the sub to the PRE-FOLD plan
    (close_snapshot), not skip the restore because the sub holds the LAST
    change's to_* while the legacy guard compared the EARLIEST's."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    pre_fold_version = sub.plan_version_id
    # Two stacked deferred downgrades: growth→school, then growth→community.
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=None, proration_mode="next_period", actor=a
    )
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="community", seats=None, proration_mode="next_period", actor=a
    )
    from app.controlplane.models.billing import SubscriptionChange

    last = (
        await db.execute(
            select(SubscriptionChange)
            .where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.proration_mode == "next_period",
            )
            .order_by(SubscriptionChange.id.desc())
            .limit(1)
        )
    ).scalar_one()
    inv1 = await _force_close(db, sub)  # rollover: folds BOTH, last-wins
    assert inv1 is not None
    await db.refresh(sub)
    assert sub.plan_version_id == last.to_plan_version_id, "fold is last-wins"
    growth_fee = _plan_lines_total(await _lines(db, inv1), "plan")
    assert growth_fee == 49900, "original close bills the pre-fold plan"

    await billing_svc.void_invoice(db, inv1, reason="stacked dispute", actor=a)
    await db.refresh(sub)
    assert sub.plan_version_id == pre_fold_version, (
        "void must rewind to the PRE-FOLD plan even with stacked deferred changes"
    )
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    assert _plan_lines_total(await _lines(db, inv2), "plan") == 49900, (
        "re-close must bill the voided period at the original (growth) fee, "
        "not the folded downgrade's"
    )
    # And the re-rollover re-applies the stacked fold (last-wins again).
    await db.refresh(sub)
    assert sub.plan_version_id == last.to_plan_version_id


@pytest.mark.asyncio
async def test_void_restore_skips_axis_after_roundtrip_forward_changes(db):
    """R135 (high): forward-window immediate changes that ROUND-TRIP back to
    the post_fold value (10→20→10) must still mark the axis as forward-owned:
    the restore skips (ID-order discriminator, same as the re-close's
    supersede), so the sub keeps the tenant's final choice instead of being
    stranded on pre_fold."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="community", interval="month", seats=30, provider="manual", actor=a
    )
    p1 = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    shift = datetime.now(UTC) - timedelta(seconds=1) - p1.period_end
    p1.period_start = p1.period_start + shift
    p1.period_end = p1.period_end + shift
    sub.current_period_start = p1.period_start
    sub.current_period_end = p1.period_end
    await db.flush()
    # Deferred seat change 30 → 40 (floors above the 25 included so the
    # invoice is non-zero — a zero-amount invoice auto-pays and cannot void).
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=40, proration_mode="next_period", actor=a
    )
    inv1 = await billing_svc.close_period_and_invoice(db, p1.id)
    assert inv1 is not None
    await db.refresh(sub)
    assert sub.seat_quantity == 40  # folded
    # Forward window: 40 → 60 → 40 (round-trip back to post_fold value).
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=60, proration_mode="immediate", actor=a
    )
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=None, seats=40, proration_mode="immediate", actor=a
    )
    await db.refresh(sub)
    assert sub.seat_quantity == 40
    # Void P1: the forward window OWNS the seats axis (two real changes with
    # id > watermark) — the restore must NOT rewind to 30.
    await billing_svc.void_invoice(db, inv1, reason="dispute", actor=a)
    await db.refresh(sub)
    assert sub.seat_quantity == 40, (
        "restore must skip a forward-owned axis even when its value equals post_fold"
    )
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    await db.refresh(sub)
    assert sub.seat_quantity == 40, "re-close must leave the tenant's final choice in force"


@pytest.mark.asyncio
async def test_reclose_replays_original_live_seat_count(db):
    """R135 (medium): the seats line's live-seat count is stamped into
    close_snapshot at the original close; a re-close after membership churn
    must bill the SAME seats charge (period membership is a historical
    fact)."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="community", interval="month", seats=40, provider="manual", actor=a
    )
    inv1 = await _force_close(db, sub)
    assert inv1 is not None
    seats1 = _plan_lines_total(await _lines(db, inv1), "seats")
    assert seats1 > 0
    assert inv1.close_snapshot.get("live_seats") is not None, "live count must be stamped"
    # Simulate interim churn by corrupting what a re-derivation WOULD see:
    # (no members were ever created for this tenant, so live=0 both times —
    # instead prove the replay path by editing the snapshot's stamped count
    # and asserting the re-close bills from the SNAPSHOT, not a fresh query.)
    snap = dict(inv1.close_snapshot)
    snap["live_seats"] = 999  # pretend 999 students were active during P
    inv1.close_snapshot = snap
    await db.flush()
    await billing_svc.void_invoice(db, inv1, reason="dispute", actor=a)
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    seats2 = _plan_lines_total(await _lines(db, inv2), "seats")
    # replayed basis: max(999, 40) - 25 included, vs fresh query max(0,40)-25
    assert seats2 > seats1, (
        f"re-close must replay the stamped live count (got {seats2}, original-shape {seats1})"
    )


@pytest.mark.asyncio
async def test_legacy_reclose_does_not_stamp_fresh_watermark(db):
    """R135 (medium): a re-close of a LEGACY void (no snapshot on the void
    invoice) must NOT stamp its re-close-time watermark as if it were the
    original close's — that watermark includes forward-window changes and
    would poison the NEXT void/re-close cycle's supersede. The re-issued
    invoice carries basis + fold outcome but NO change_watermark key."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="growth", interval="month", seats=0, provider="manual", actor=a
    )
    await billing_svc.change_plan(
        db, tenant, sub, plan_key="school", seats=None, proration_mode="next_period", actor=a
    )
    inv1 = await _force_close(db, sub)
    assert inv1 is not None
    # Make inv1 a LEGACY invoice (pre-snapshot era).
    inv1.close_snapshot = None
    await db.flush()
    await billing_svc.void_invoice(db, inv1, reason="legacy dispute", actor=a)
    inv2 = await billing_svc.close_period_and_invoice(db, inv1.billing_period_id)
    assert inv2 is not None
    snap = inv2.close_snapshot or {}
    assert "change_watermark" not in snap, (
        "legacy re-close must not stamp a fresh watermark as the original's"
    )
    # basis + fold outcome still stamped (usable by later restores)
    assert "start_version_id" in snap
    assert "post_fold_version_id" in snap


@pytest.mark.asyncio
async def test_credit_note_idempotency_key(db):
    """R135: a retried credit-note POST created a SECOND note and
    double-refunded (each retry minted a fresh cn:{new_id} ledger key, so the
    ledger dedup could never fire). A keyed retry with the same amount must
    return the ORIGINAL note; the same key with a different amount is a 409."""
    from datetime import timedelta as _td

    from app.controlplane.models.billing import CreditNote

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    from app.controlplane.services.billing import _add_interval

    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    period.period_start = datetime.now(UTC) - _td(days=40)
    period.period_end = _add_interval(period.period_start, "month")
    sub.current_period_start = period.period_start
    sub.current_period_end = period.period_end
    await db.flush()
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    assert invoice is not None
    await db.refresh(invoice)
    assert invoice.total_minor == 19900
    key = f"cnkey-{ULID()}"
    n1 = await billing_svc.issue_credit_note(
        db,
        invoice,
        amount_minor=3000,
        reason="partial refund",
        actor=_actor(user),
        idempotency_key=key,
    )
    await db.refresh(invoice)
    assert invoice.amount_due_minor == 16900
    # Retry (same key, same amount) → the ORIGINAL note, nothing re-applied.
    n2 = await billing_svc.issue_credit_note(
        db,
        invoice,
        amount_minor=3000,
        reason="partial refund (retry)",
        actor=_actor(user),
        idempotency_key=key,
    )
    assert n2.id == n1.id
    await db.refresh(invoice)
    assert invoice.amount_due_minor == 16900, "the retry must not double-apply"
    notes = (
        (
            await db.execute(
                select(CreditNote).where(
                    CreditNote.invoice_id == invoice.id, CreditNote.idempotency_key == key
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(notes) == 1, f"{len(notes)} notes landed for one key"
    # Same key, different amount → parameter divergence, not a silent replay.
    with pytest.raises(AppError) as exc:
        await billing_svc.issue_credit_note(
            db,
            invoice,
            amount_minor=4000,
            reason="different amount",
            actor=_actor(user),
            idempotency_key=key,
        )
    assert exc.value.code == "IDEMPOTENCY_CONFLICT"
    # Unkeyed calls keep the legacy behavior (each mints a new note).
    n3 = await billing_svc.issue_credit_note(
        db, invoice, amount_minor=1000, reason="unkeyed", actor=_actor(user)
    )
    assert n3.id != n1.id
    # R136: a keyed retry AFTER the invoice was voided replays the original
    # note (the operation DID succeed) instead of 409'ing; a NEW note on the
    # void invoice is still rejected.
    await billing_svc.void_invoice(db, invoice, reason="redo cycle", actor=_actor(user))
    n4 = await billing_svc.issue_credit_note(
        db,
        invoice,
        amount_minor=3000,
        reason="late retry",
        actor=_actor(user),
        idempotency_key=key,
    )
    assert n4.id == n1.id
    with pytest.raises(AppError) as exc_void:
        await billing_svc.issue_credit_note(
            db,
            invoice,
            amount_minor=500,
            reason="fresh note on void",
            actor=_actor(user),
            idempotency_key=f"cnk2-{ULID()}",
        )
    assert exc_void.value.code == "INVOICE_NOT_OPEN"


@pytest.mark.asyncio
async def test_gap_change_seat_basis_is_current_not_elapsed_period_start(db):
    """R135 (extends R131[5]): a gap change (period elapsed, hourly close not
    yet run) is billed by the NEXT period's close, whose seats basis is this
    change's own from_* — the sub's CURRENT seats. With a prior mid-period
    change, the ELAPSED period-start basis made the approved seat proration
    diverge from the invoiced one (the R129[M5]/R130[2] parity class)."""
    from datetime import timedelta as _td
    from decimal import ROUND_HALF_UP, Decimal

    from app.controlplane.models.billing import SubscriptionChange

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=300,
        provider="manual",
        actor=_actor(user),
    )
    # Prior mid-period immediate seat change 300 → 250.
    await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key=None,
        seats=250,
        proration_mode="immediate",
        actor=_actor(user),
    )
    from app.controlplane.services.billing import _add_interval

    # Shift the period fully into the past (gap), keeping the prior change
    # INSIDE the elapsed period so _period_start_seat_basis resolves to its
    # from_seats=300 — the wrong basis for the gap window.
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"
            )
        )
    ).scalar_one()
    period.period_start = datetime.now(UTC) - _td(days=40)
    period.period_end = _add_interval(period.period_start, "month")
    sub.current_period_start = period.period_start
    sub.current_period_end = period.period_end
    prior = (
        await db.execute(
            select(SubscriptionChange)
            .where(SubscriptionChange.subscription_id == sub.id)
            .order_by(SubscriptionChange.id)
        )
    ).scalars().all()[-1]
    prior.effective_at = datetime.now(UTC) - _td(days=20)
    await db.flush()
    gap_start = sub.current_period_end
    gap_end = _add_interval(gap_start, "month")
    # Gap change: seats 250 → 400, previewed against the NEXT window.
    res = await billing_svc.change_plan(
        db,
        tenant,
        sub,
        plan_key=None,
        seats=400,
        proration_mode="immediate",
        actor=_actor(user),
    )
    preview = res["proration"]
    gap_change = (
        await db.execute(
            select(SubscriptionChange)
            .where(SubscriptionChange.subscription_id == sub.id)
            .order_by(SubscriptionChange.id)
        )
    ).scalars().all()[-1]
    at = gap_change.effective_at
    total_days = max((gap_end - gap_start).days, 1)
    seat_days = max(min((gap_end - at).days, total_days), 0)
    assert seat_days > 0, "sanity: the gap window must have remaining days"

    # school seed: included 200, overage 500/seat; no live students (band =
    # old-seats floor). correct = (max(400, basis) − 200) × 500 = 100000.
    def _expected(basis: int) -> int:
        covered = max(basis - 200, 0) * 500
        correct = max(max(400, basis) - 200, 0) * 500
        return int(
            (Decimal(correct - covered) / Decimal(total_days) * seat_days).quantize(
                Decimal("1"), rounding=ROUND_HALF_UP
            )
        )

    expected_current = _expected(250)  # sub's CURRENT seats — the fix
    expected_elapsed = _expected(300)  # elapsed period-start basis — the bug
    assert expected_current != expected_elapsed, "sanity: the bases must diverge"
    assert preview["seat_proration_minor"] == expected_current, (
        f"gap preview used the elapsed-period basis: {preview['seat_proration_minor']} "
        f"(elapsed would be {expected_elapsed})"
    )


@pytest.mark.asyncio
async def test_stripe_webhook_out_of_order_status_events_ignored(db):
    """R167: Stripe delivers events with no ordering guarantee. A STALE
    invoice.paid arriving after a newer invoice.payment_failed must NOT
    resurrect the subscription to active — the status handlers gate on the
    event's created-time high-water mark. Applied directly through
    _apply_webhook_event with explicit occurred_at (the mock signer path
    carries no timestamp)."""
    from datetime import timedelta as _td

    from app.controlplane.services.billing import _apply_webhook_event
    from app.controlplane.services.billing_providers.base import ParsedWebhookEvent

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user),
    )
    sub.provider = "stripe"
    sub.external_ref = f"sub_{ULID()}"
    sub.status = "active"
    await db.flush()

    t1 = datetime.now(UTC) - _td(hours=2)  # OLD (cycle N)
    t2 = datetime.now(UTC) - _td(hours=1)  # NEWER (cycle N)
    t3 = datetime.now(UTC)                 # NEWEST (cycle N+1)

    def _evt(etype, occurred):
        return ParsedWebhookEvent(
            external_event_id=f"evt_{ULID()}",
            event_type=etype,
            data={"subscription": sub.external_ref},
            occurred_at=occurred,
        )

    # 1. payment_failed @ t2 → past_due, hwm=t2
    await _apply_webhook_event(db, "stripe", _evt("invoice.payment_failed", t2))
    await db.refresh(sub)
    assert sub.status == "past_due", "failed event must move sub to past_due"
    assert sub.last_billing_event_at == t2

    # 2. STALE paid @ t1 (< t2) → IGNORED, sub stays past_due
    handled = await _apply_webhook_event(db, "stripe", _evt("invoice.paid", t1))
    await db.refresh(sub)
    assert handled is True  # recorded, not errored
    assert sub.status == "past_due", "stale paid event must NOT resurrect the sub"
    assert sub.last_billing_event_at == t2, "hwm must not regress on a stale event"

    # 3. NEWER paid @ t3 → active, hwm=t3
    await _apply_webhook_event(db, "stripe", _evt("invoice.paid", t3))
    await db.refresh(sub)
    assert sub.status == "active", "a newer paid event must reactivate"
    assert sub.last_billing_event_at == t3


# ── R203: preview↔invoice DIFFERENTIAL test ──────────────────
# Two independent production paths compute the customer-facing net of a
# mid-period immediate plan change: change_plan() returns the preview shown
# at approval time, and close_period_and_invoice() emits the proration lines
# actually billed. If they diverge by a cent, the customer approved a number
# they never pay (or pay more than). Prior tests hand-computed one side; this
# drives BOTH on randomized economics and asserts agreement.


async def _seed_plan(db, user, key, *, amount, included, seat_price):
    from app.controlplane.models.plan import PlanPrice
    from app.controlplane.services import plans as plan_svc

    plan = await plan_svc.create_plan(
        db, key=key, name=key, description=None, actor=_actor(user)
    )
    draft = await plan_svc.create_draft_version(db, plan, created_by=user.id)
    draft.entitlements = {"max_active_learners": 1000, "max_instructors": 100}
    db.add(
        PlanPrice(
            plan_version_id=draft.id,
            currency="USD",
            interval="month",
            amount_minor=amount,
            included_seats=included,
            overage_seat_amount_minor=seat_price,
        )
    )
    await db.flush()
    await plan_svc.activate_version(db, draft, actor=_actor(user))
    return plan.key


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "old_amt,new_amt,old_inc,new_inc,old_sp,new_sp,seats,day",
    [
        (10000, 20000, 5, 5, 500, 500, 0, 15),    # pure plan upgrade, no seats
        (20000, 10000, 5, 5, 500, 500, 0, 15),    # downgrade (immediate)
        (10000, 8000, 10, 2, 500, 500, 10, 15),   # R123[C0]: shrink included, live seats
        (10000, 20000, 5, 8, 300, 700, 12, 10),   # included + price both change
        (15000, 15000, 3, 3, 400, 400, 7, 20),    # same fee, seat band only
        (9999, 33333, 1, 9, 111, 999, 5, 3),      # odd numbers → rounding stress
    ],
)
async def test_preview_matches_invoice_proration(
    db, old_amt, new_amt, old_inc, new_inc, old_sp, new_sp, seats, day
):
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
    )

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    uniq = str(ULID()).lower()[:8]
    old_key = await _seed_plan(db, user, f"old-{uniq}", amount=old_amt, included=old_inc, seat_price=old_sp)
    new_key = await _seed_plan(db, user, f"new-{uniq}", amount=new_amt, included=new_inc, seat_price=new_sp)

    # `seats` live STUDENT members in one org of the tenant → drives billable_seats
    org = Organization(tenant_id=tenant.id, name=f"o{uniq}", slug=f"o{uniq}", created_by=user.id)
    db.add(org)
    await db.flush()
    for _i in range(seats):
        m = await _mk_user(db)
        db.add(OrgMember(org_id=org.id, user_id=m.id, role=OrgRole.STUDENT, status=MemberStatus.ACTIVE))
    await db.flush()

    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key=old_key, interval="month", seats=0, provider="manual", actor=a
    )
    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    # Anchor a clean 30-day window; the change lands on `day`.
    period.period_start = datetime(2026, 6, 1, tzinfo=UTC)
    period.period_end = datetime(2026, 7, 1, tzinfo=UTC)
    sub.current_period_start = period.period_start
    sub.current_period_end = period.period_end
    await db.flush()

    # Freeze the change clock to `day` so preview and close agree on `at`.
    import app.controlplane.services.billing as bmod

    real_now = bmod._now
    bmod._now = lambda: datetime(2026, 6, day, tzinfo=UTC)
    try:
        result = await billing_svc.change_plan(
            db, tenant, sub, plan_key=new_key, seats=None, proration_mode="immediate", actor=a
        )
    finally:
        bmod._now = real_now
    preview_net = result["proration"]["net_minor"]
    assert result["mode"] == "immediate"

    # Close the period; sum the change's actual invoice contribution =
    # per-segment plan proration + seat proration lines (the base plan line is
    # the full-period NEW plan fee, not part of the change delta).
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    lines = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == invoice.id)))
        .scalars()
        .all()
    )
    invoiced_change_net = sum(
        line.amount_minor for line in lines if line.line_type == "proration"
    )
    assert invoiced_change_net == preview_net, (
        f"preview shown {preview_net} but invoice billed {invoiced_change_net} "
        f"[lines: {[(ln.line_type, ln.amount_minor) for ln in lines]}]"
    )


@pytest.mark.asyncio
async def test_scan_due_periods_dedups_live_close_messages(db):
    """R260: while the outbox is backlogged, every hourly scan re-enqueued
    the same still-open periods — duplicate period.close_due messages piling
    up unboundedly. A live (pending/processing) close message dedups."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))
    period = (
        await db.execute(
            select(BillingPeriod).where(
                BillingPeriod.subscription_id == sub.id, BillingPeriod.status == "open"))
    ).scalar_one()
    period.period_end = datetime.now(UTC) - timedelta(hours=1)
    await db.flush()

    def count_msgs():
        return (
            db.execute(
                select(OutboxMessage).where(
                    OutboxMessage.topic == "period.close_due",
                    OutboxMessage.payload["billing_period_id"].astext == period.id,
                )
            )
        )

    n1 = await billing_svc.scan_due_periods(db)
    msgs = (await count_msgs()).scalars().all()
    assert len(msgs) == 1

    await billing_svc.scan_due_periods(db)               # re-scan: deduped
    msgs = (await count_msgs()).scalars().all()
    assert len(msgs) == 1
    assert n1 >= 1

    msgs[0].status = "done"                              # processed → closes...
    await db.flush()
    await billing_svc.scan_due_periods(db)               # ...but period still open
    msgs = (await count_msgs()).scalars().all()
    assert len(msgs) == 2                                # re-enqueue is allowed again


@pytest.mark.asyncio
async def test_provider_initiated_cancel_webhook_branch(db):
    """R265: customer.subscription.deleted (dunning exhausted / dashboard
    cancel) had no sentinel — the sub must cancel, the open period must
    truncate to now and enqueue its close (R101[H21]'s webhook sibling:
    cancelled subs fall out of scan_due_periods, stranding the final partial
    invoice), and tenant owners must be notified (R113[M5]). Unknown ref → no-op."""
    from types import SimpleNamespace

    from app.controlplane.models.outbox import OutboxMessage
    from app.controlplane.services.billing import _apply_webhook_event
    from app.models.notification import Notification

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))
    sub.external_ref = f"sub_ext_{ULID()}"
    await db.flush()

    # unknown external ref → unhandled, nothing changes
    ghost = SimpleNamespace(event_type="customer.subscription.deleted",
                            data={"id": "sub_ghost"})
    assert await _apply_webhook_event(db, "stripe", ghost) is False

    parsed = SimpleNamespace(event_type="customer.subscription.deleted",
                             data={"id": sub.external_ref})
    handled = await _apply_webhook_event(db, "stripe", parsed)
    assert handled is True
    await db.refresh(sub)
    assert sub.status == "cancelled" and sub.cancelled_at is not None

    period = (
        await db.execute(
            select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    assert period.period_end <= datetime.now(UTC)          # truncated
    close_msgs = (
        (await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "period.close_due",
                OutboxMessage.payload["billing_period_id"].astext == period.id)))
        .scalars().all()
    )
    assert len(close_msgs) >= 1                            # final invoice enqueued

    notes = (
        (await db.execute(
            select(Notification).where(
                Notification.user_id == user.id,
                Notification.type == "billing.subscription_cancelled")))
        .scalars().all()
    )
    assert len(notes) >= 1                                 # owner told (R113[M5])

    # replay: sub already cancelled → unhandled, no duplicate close
    assert await _apply_webhook_event(db, "stripe", parsed) is False


@pytest.mark.asyncio
async def test_push_provider_handler_arcs(db, monkeypatch):
    """R266: handle_subscription_push_provider carried five fixed behaviors
    with zero tests. Pins: the R113[C0] cancel-flag push (a plan push must
    not silently un-cancel a pending provider cancellation), the missing-
    price no-crash arc, and the R131 terminal-tolerance rework (a dead
    provider sub is swallowed ONLY when the platform row is terminal too —
    a live row must dead-letter loudly)."""
    from app.controlplane.services.billing import handle_subscription_push_provider
    from app.controlplane.services.billing_providers.mock import MockProvider

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))

    # guards: unknown sub / manual provider / missing ref → silent no-ops
    await handle_subscription_push_provider(db, {"subscription_id": str(ULID())})
    await handle_subscription_push_provider(db, {"subscription_id": sub.id})

    sub.provider = "mock"
    sub.external_ref = f"mock_sub_{ULID()}"
    sub.cancel_at_period_end = True
    await db.flush()

    calls: list[dict] = []

    async def record(self, external_ref, new_price_ref, seat_quantity,
                     cancel_at_period_end=False):
        calls.append(dict(ref=external_ref, price=new_price_ref,
                          seats=seat_quantity, cape=cancel_at_period_end))

    monkeypatch.setattr(MockProvider, "change_subscription", record)
    await handle_subscription_push_provider(db, {"subscription_id": sub.id})
    assert len(calls) == 1
    assert calls[0]["ref"] == sub.external_ref
    assert calls[0]["cape"] is True                       # R113[C0]

    # missing PlanPrice (unpriced currency) → logged, no crash, no push
    sub.currency = "XXX"
    await db.flush()
    await handle_subscription_push_provider(db, {"subscription_id": sub.id})
    assert len(calls) == 1
    sub.currency = "USD"
    await db.flush()

    # R131: provider says the sub is dead
    class InvalidRequestError(Exception):
        pass

    async def dead(self, *a, **kw):
        raise InvalidRequestError("No such subscription: sub_x")

    monkeypatch.setattr(MockProvider, "change_subscription", dead)
    with pytest.raises(InvalidRequestError):              # LIVE platform row → raise
        await handle_subscription_push_provider(db, {"subscription_id": sub.id})

    sub.status = "cancelled"
    await db.flush()
    await handle_subscription_push_provider(db, {"subscription_id": sub.id})  # swallowed


@pytest.mark.asyncio
async def test_cancel_provider_handler_arcs(db, monkeypatch):
    """R267: handle_subscription_cancel_provider — the R123[H6] reactivation
    guard (a retried cancel(at_end) after a successful reactivate must NOT
    re-arm the provider cancel), the R123[M12/M16] already-terminal success
    mapping, and transient failures still raising for outbox retry."""
    from app.controlplane.services.billing import handle_subscription_cancel_provider
    from app.controlplane.services.billing_providers.mock import MockProvider

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))
    sub.provider = "mock"
    sub.external_ref = f"mock_sub_{ULID()}"
    await db.flush()

    calls: list[tuple] = []

    async def record(self, external_ref, at_period_end):
        calls.append((external_ref, at_period_end))

    monkeypatch.setattr(MockProvider, "cancel_subscription", record)

    # bad payloads → silent no-ops
    await handle_subscription_cancel_provider(db, {"provider": "manual", "external_ref": "x"})
    await handle_subscription_cancel_provider(db, {"provider": "mock", "external_ref": ""})
    assert calls == []

    # R123[H6]: at_end cancel retried AFTER reactivation → skipped
    assert sub.status == "active" and not sub.cancel_at_period_end
    await handle_subscription_cancel_provider(db, {
        "provider": "mock", "external_ref": sub.external_ref,
        "at_period_end": True, "subscription_id": sub.id})
    assert calls == []                                     # obsolete cancel skipped

    # pending cancellation → executes with the flag
    sub.cancel_at_period_end = True
    await db.flush()
    await handle_subscription_cancel_provider(db, {
        "provider": "mock", "external_ref": sub.external_ref,
        "at_period_end": True, "subscription_id": sub.id})
    assert calls == [(sub.external_ref, True)]

    # immediate cancel executes regardless of platform state
    await handle_subscription_cancel_provider(db, {
        "provider": "mock", "external_ref": sub.external_ref,
        "at_period_end": False, "subscription_id": sub.id})
    assert calls[-1] == (sub.external_ref, False)

    # R123[M12/M16]: provider already-terminal → success; transient → raise
    class InvalidRequestError(Exception):
        pass

    async def already_gone(self, *a, **kw):
        raise InvalidRequestError("No such subscription: sub_x")

    monkeypatch.setattr(MockProvider, "cancel_subscription", already_gone)
    await handle_subscription_cancel_provider(db, {
        "provider": "mock", "external_ref": sub.external_ref, "at_period_end": False})

    async def transient(self, *a, **kw):
        raise RuntimeError("connection reset")

    monkeypatch.setattr(MockProvider, "cancel_subscription", transient)
    with pytest.raises(RuntimeError):
        await handle_subscription_cancel_provider(db, {
            "provider": "mock", "external_ref": sub.external_ref, "at_period_end": False})


@pytest.mark.asyncio
async def test_reactivate_subscription_arcs(db):
    """R268: the direct un-cancel path (R101[H16/H17]) had no test — a
    pending-cancellation sub reactivates (flag cleared, change recorded,
    provider push enqueued); anything else is a 409."""
    from app.controlplane.models.billing import SubscriptionChange
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=a)

    with pytest.raises(AppError) as e:                     # active sub → 409
        await billing_svc.reactivate_subscription(db, tenant, sub, actor=a)
    assert e.value.code == "SUBSCRIPTION_STATUS_CONFLICT" and e.value.status_code == 409

    sub.provider = "mock"
    sub.external_ref = f"mock_sub_{ULID()}"
    await db.flush()
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=True, actor=a)
    await db.refresh(sub)
    assert sub.status == "cancel_at_period_end"

    sub = await billing_svc.reactivate_subscription(db, tenant, sub, actor=a)
    assert sub.status == "active" and sub.cancel_at_period_end is False
    chg = (
        (await db.execute(
            select(SubscriptionChange).where(
                SubscriptionChange.subscription_id == sub.id,
                SubscriptionChange.change_type == "reactivate")))
        .scalars().all()
    )
    assert len(chg) == 1
    pushes = (
        (await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "subscription.push_provider",
                OutboxMessage.payload["subscription_id"].astext == sub.id)))
        .scalars().all()
    )
    assert len(pushes) >= 1                                # R101[H17] via outbox

    # immediate-cancelled sub can NOT be resurrected
    await billing_svc.cancel_subscription(db, tenant, sub, at_period_end=False, actor=a)
    await db.refresh(sub)
    assert sub.status == "cancelled"
    with pytest.raises(AppError) as e:
        await billing_svc.reactivate_subscription(db, tenant, sub, actor=a)
    assert e.value.status_code == 409


def test_billing_event_hwm_pure_boundaries():
    """R271: the R167 event-ordering pair, pinned at the boundaries — an
    event at EXACTLY the high-water mark is not stale (equal-time retries
    still apply; dedup lives on the event unique key), the mark advances only
    on strictly newer, and unknown occurred_at neither stales nor advances.

    Mutation status: 6/7 killed; the survivor (advance > → >=) is provably
    equivalent — an equal-time "advance" assigns the identical value.
    """
    from types import SimpleNamespace

    from app.controlplane.services.billing import (
        _advance_billing_event_hwm,
        _is_stale_billing_event,
    )

    t1 = datetime(2026, 9, 1, tzinfo=UTC)
    t2 = datetime(2026, 9, 2, tzinfo=UTC)

    sub = SimpleNamespace(last_billing_event_at=None)
    ev = SimpleNamespace(occurred_at=None)
    assert _is_stale_billing_event(sub, ev) is False       # unknown time never stale
    _advance_billing_event_hwm(sub, ev)
    assert sub.last_billing_event_at is None               # and never advances

    ev1 = SimpleNamespace(occurred_at=t1)
    assert _is_stale_billing_event(sub, ev1) is False      # first event
    _advance_billing_event_hwm(sub, ev1)
    assert sub.last_billing_event_at == t1

    assert _is_stale_billing_event(sub, ev1) is False      # EQUAL time: not stale
    _advance_billing_event_hwm(sub, ev1)
    assert sub.last_billing_event_at == t1                 # equal does not re-advance

    ev0 = SimpleNamespace(occurred_at=t1 - timedelta(seconds=1))
    assert _is_stale_billing_event(sub, ev0) is True       # older → stale
    _advance_billing_event_hwm(sub, ev0)
    assert sub.last_billing_event_at == t1                 # never regresses

    ev2 = SimpleNamespace(occurred_at=t2)
    assert _is_stale_billing_event(sub, ev2) is False
    _advance_billing_event_hwm(sub, ev2)
    assert sub.last_billing_event_at == t2


@pytest.mark.asyncio
async def test_subscription_http_self_service_guards(db):
    """R293: the tenant-facing subscription endpoints' OWN guards (all prior
    tests drive the service directly). A non-platform tenant owner cannot
    self-mint a MANUAL subscription (which never charges — a billing bypass):
    MANUAL_BILLING_MODE 409. change/cancel/reactivate with no live sub → 404.
    A change with neither plan_key nor seats → 'Nothing to change' 422."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.core.security import create_access_token
    from app.main import app

    owner = await _mk_user(db)
    tenant = await _mk_tenant(db, owner, status=TenantStatus.ACTIVE)
    await db.commit()
    token = create_access_token(owner.id, owner.email, "student")
    tid = tenant.id

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}

            # self-mint of a manual subscription → 409 (billing bypass guard)
            r = await c.post(f"/api/v1/tenants/{tid}/subscription", headers=hdr,
                             json={"plan_key": "school", "interval": "month",
                                   "seats": 0, "provider": "manual"})
            assert r.status_code == 409, r.text
            assert r.json()["error"]["code"] == "MANUAL_BILLING_MODE"

            # change/cancel/reactivate with no live subscription → 404
            for path, payload in (
                ("/subscription/change", {"seats": 5}),
                ("/subscription/cancel", {"at_period_end": True}),
                ("/subscription/reactivate", {}),
            ):
                r = await c.post(f"/api/v1/tenants/{tid}{path}", headers=hdr, json=payload)
                assert r.status_code == 404, (path, r.text)
                assert r.json()["error"]["code"] == "SUBSCRIPTION_NOT_FOUND"
    finally:
        app.router.lifespan_context = orig

    # now give the tenant a live sub (service path) and test the empty-change arc
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(owner))
    await db.commit()

    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}
            r = await c.post(f"/api/v1/tenants/{tid}/subscription/change",
                             headers=hdr, json={})
            assert r.status_code == 422, r.text
            assert r.json()["error"]["code"] == "VALIDATION_ERROR"
    finally:
        app.router.lifespan_context = orig
        async with AsyncSessionLocal() as clean:
            s2 = await clean.get(type(sub), sub.id)
            if s2 is not None:
                await clean.delete(s2)
                await clean.commit()


@pytest.mark.asyncio
async def test_webhook_failed_handler_records_event_and_dedups_replay(db, monkeypatch):
    """R310: the R42[7] SAVEPOINT isolation. If the handler RAISES, the
    just-inserted BillingWebhookEvent row must SURVIVE (status='failed'),
    never vanish with a transaction rollback — otherwise the provider's
    retry re-processes a possibly half-applied event. And a redelivery of the
    same event id short-circuits as a duplicate: the handler is NOT re-run."""
    from app.controlplane.models.billing import BillingWebhookEvent
    from app.controlplane.services import billing as bsvc
    from app.controlplane.services.billing_providers.mock import sign_mock_event

    calls = {"n": 0}

    async def boom(db_, provider, parsed):
        # a DB-LEVEL abort (not a plain Python raise) — this is the R42[7]
        # scenario: it poisons the transaction, so without the SAVEPOINT the
        # subsequent event.status='failed' flush would itself fail and the
        # event row would vanish with the rollback.
        from sqlalchemy import text as _text

        calls["n"] += 1
        await db_.execute(_text("SELECT 1 / 0"))
        return True

    monkeypatch.setattr(bsvc, "_apply_webhook_event", boom)

    event_id = f"mevt_{ULID()}"
    payload = {"id": event_id, "type": "checkout.completed", "data": {"id": "x"}}
    raw, sig = sign_mock_event(payload)
    headers = {"x-mock-signature": sig}

    r1 = await bsvc.process_webhook(db, "mock", headers, raw)
    assert r1["duplicate"] is False and r1["status"] == "failed"
    assert calls["n"] == 1

    # the event row survived the handler failure (recorded, not rolled back)
    row = (
        await db.execute(
            select(BillingWebhookEvent).where(
                BillingWebhookEvent.provider == "mock",
                BillingWebhookEvent.external_event_id == event_id))
    ).scalar_one()
    assert row.status == "failed" and row.error

    # redelivery → duplicate short-circuit; handler is NOT called again
    r2 = await bsvc.process_webhook(db, "mock", headers, raw)
    assert r2["duplicate"] is True
    assert calls["n"] == 1  # never re-applied


@pytest.mark.asyncio
async def test_bill_via_invoice_purchase_becomes_license_line_at_close(db):
    """R316: the content-license invoice path. A paid bill_via_invoice
    purchase (payment_method='invoice', invoice_id NULL) must be assembled
    into a 'license' invoice line at the tenant's next period close, at
    amount_minor, with purchase.invoice_id stamped — and a SECOND close must
    NOT re-bill it (the invoice_id stamp is the dedup). Only the paid-and-
    unbilled state qualifies; a still-pending invoice purchase is skipped."""
    from app.controlplane.models.billing import InvoiceLine
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))

    listing = MarketplaceListing(
        product_type="skill_pack", product_id=str(ULID()),
        seller_org_id="01JFAKEORGFAKEORGFAKEORGFA", seller_tenant_id=str(ULID()),
        offer_type="paid", price_minor=7000, currency="USD",
        license_scope="organization", platform_commission_pct=30,
        bill_via_invoice=True, status="active", created_by=user.id)
    db.add(listing)
    await db.flush()

    def mk_purchase(status, amount=7000):
        return MarketplacePurchase(
            listing_id=listing.id, buyer_tenant_id=tenant.id,
            buyer_org_id="01JFAKEORGFAKEORGFAKEORGFA", purchaser_user_id=user.id,
            status=status, amount_minor=amount, currency="USD",
            economics_snapshot={}, payment_method="invoice", invoice_id=None)

    paid = mk_purchase("paid")
    pending = mk_purchase("pending", amount=999)   # not yet paid → must be skipped
    db.add_all([paid, pending])
    await db.flush()

    inv = await _force_close(db, sub)
    assert inv is not None
    lic_lines = (
        (await db.execute(
            select(InvoiceLine).where(
                InvoiceLine.invoice_id == inv.id, InvoiceLine.line_type == "license")))
        .scalars().all()
    )
    assert len(lic_lines) == 1
    assert lic_lines[0].amount_minor == 7000
    assert int(lic_lines[0].quantity) == 1  # R346: one license, one unit
    await db.refresh(paid)
    await db.refresh(pending)
    assert paid.invoice_id == inv.id          # stamped
    assert pending.invoice_id is None         # unpaid → not billed

    # a SECOND close must not re-bill the already-invoiced license
    inv2 = await _force_close(db, sub)
    if inv2 is not None:
        relic = (
            (await db.execute(
                select(InvoiceLine).where(
                    InvoiceLine.invoice_id == inv2.id,
                    InvoiceLine.line_type == "license")))
            .scalars().all()
        )
        assert relic == [], "already-invoiced license was re-billed on the next close"


@pytest.mark.asyncio
async def test_plan_change_boundaries_and_provider_gates(db):
    """R347 (mutation survivors): (1) an EQUAL-price plan change takes the
    upgrade path (immediate — GtE, not Gt); (2) an explicit next_period
    change schedules effective_at at the period end and does NOT flip the
    sub; (3) a target price with NULL seat overage prices seats at 0, never
    None-crashes; (4) MANUAL-provider change/cancel enqueue NO provider push;
    (5) statuses: duplicate sub 409, unknown provider 422, double-cancel 409.
    (6) provider gates on cancel (topic subscription.cancel_provider) and
    reactivate (push_provider): mock-no-ref notifies nothing, a ref pushes.
    Deferred (documented): the gap-window price-dim mutants (change landing
    after period_end — R135's gap branch) need live-seat scaffolding to be
    observable (all seat math is zero without students), and the reactivate
    period_end>now instant is a sub-µs clock race."""
    from app.controlplane.models.outbox import OutboxMessage

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    ka = await _seed_plan(db, user, f"r347a-{str(ULID()).lower()[:8]}",
                          amount=10000, included=5, seat_price=500)
    kb = await _seed_plan(db, user, f"r347b-{str(ULID()).lower()[:8]}",
                          amount=10000, included=3, seat_price=300)   # EQUAL price
    kc = await _seed_plan(db, user, f"r347c-{str(ULID()).lower()[:8]}",
                          amount=4000, included=0, seat_price=None)   # NULL overage

    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key=ka, interval="month", seats=0,
        provider="manual", actor=_actor(user))
    v_a = sub.plan_version_id

    # (5) unknown provider → 422
    t2 = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    with pytest.raises(AppError) as e422:
        await billing_svc.start_subscription(
            db, t2, plan_key=ka, interval="month", seats=0,
            provider="carrier_pigeon", actor=_actor(user))
    assert e422.value.status_code == 422
    # duplicate sub → 409 with status
    with pytest.raises(AppError) as e409:
        await billing_svc.start_subscription(
            db, tenant, plan_key=kb, interval="month", seats=0,
            provider="manual", actor=_actor(user))
    assert e409.value.code == "SUBSCRIPTION_EXISTS" and e409.value.status_code == 409

    # (1) equal-price change → immediate (upgrade path), sub flips NOW
    res = await billing_svc.change_plan(
        db, tenant, sub, plan_key=kb, seats=None, proration_mode=None,
        actor=_actor(user))
    assert res["mode"] == "immediate"
    await db.refresh(sub)
    assert sub.plan_version_id != v_a

    # (2) explicit next_period change: scheduled at period end, sub unchanged
    from app.controlplane.models.billing import SubscriptionChange

    v_b = sub.plan_version_id
    res2 = await billing_svc.change_plan(
        db, tenant, sub, plan_key=kc, seats=None, proration_mode="next_period",
        actor=_actor(user))
    assert res2["mode"] == "next_period"
    await db.refresh(sub)
    assert sub.plan_version_id == v_b                  # not flipped yet
    change = (
        await db.execute(
            select(SubscriptionChange)
            .where(SubscriptionChange.subscription_id == sub.id,
                   SubscriptionChange.proration_mode == "next_period")
            .order_by(SubscriptionChange.created_at.desc()).limit(1))
    ).scalars().first()
    assert change.effective_at == sub.current_period_end

    # (3) NULL seat-overage target, immediate → no crash, seat price 0
    res3 = await billing_svc.change_plan(
        db, tenant, sub, plan_key=kc, seats=None, proration_mode="immediate",
        actor=_actor(user))
    assert res3["proration"]["seat_proration_minor"] == 0

    # (4) manual provider: NO provider-push outbox rows anywhere in the flow
    pushes = (
        await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "subscription.push_provider"))
    ).scalars().all()
    assert all(m.payload.get("subscription_id") != sub.id for m in pushes)

    # provider-gate arcs (direct provider/ref flips on the same sub):
    # a MOCK sub WITHOUT an external ref never pushes (the Or-mutant does) …
    sub.provider = "mock"
    sub.external_ref = None
    await db.flush()
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=kb, seats=None, proration_mode="immediate",
        actor=_actor(user))
    pushes = (
        await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "subscription.push_provider"))
    ).scalars().all()
    assert all(m.payload.get("subscription_id") != sub.id for m in pushes)
    # … a MOCK sub WITH a ref pushes and is NOT stripe-price-gated …
    sub.external_ref = "mock-ref-1"
    await db.flush()
    await billing_svc.change_plan(
        db, tenant, sub, plan_key=kc, seats=None, proration_mode="immediate",
        actor=_actor(user))
    pushes = (
        await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "subscription.push_provider"))
    ).scalars().all()
    assert any(m.payload.get("subscription_id") == sub.id for m in pushes)
    # … and a STRIPE sub changing to a plan with no Stripe price ref → 409
    sub.provider = "stripe"
    await db.flush()
    with pytest.raises(AppError) as e_sp:
        await billing_svc.change_plan(
            db, tenant, sub, plan_key=ka, seats=None, proration_mode="immediate",
            actor=_actor(user))
    assert e_sp.value.code == "PLAN_NOT_AVAILABLE" and e_sp.value.status_code == 409
    sub.provider = "manual"
    sub.external_ref = None
    await db.flush()

    # (5) immediate cancel then a second cancel → guarded-update 409
    # cancel with mock-no-ref: gate stays closed (no push from cancel)
    sub.provider = "mock"
    await db.flush()

    async def _topic_count(topic, sid):
        rows = (
            await db.execute(
                select(OutboxMessage).where(OutboxMessage.topic == topic))
        ).scalars().all()
        return sum(1 for m in rows if m.payload.get("subscription_id") == sid)

    before = await _topic_count("subscription.cancel_provider", sub.id)
    await billing_svc.cancel_subscription(
        db, tenant, sub, at_period_end=False, actor=_actor(user))
    # mock-no-ref cancel notifies no provider
    assert await _topic_count("subscription.cancel_provider", sub.id) == before

    # reactivate gate (un-cancel push): schedule-cancel a fresh manual sub,
    # flip to mock-no-ref, reactivate → no provider push
    t3 = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub3, _ = await billing_svc.start_subscription(
        db, t3, plan_key=ka, interval="month", seats=0,
        provider="manual", actor=_actor(user))
    await billing_svc.cancel_subscription(
        db, t3, sub3, at_period_end=True, actor=_actor(user))
    sub3.provider = "mock"
    sub3.external_ref = None
    await db.flush()
    before3 = await _topic_count("subscription.push_provider", sub3.id)
    await billing_svc.reactivate_subscription(db, t3, sub3, actor=_actor(user))
    assert await _topic_count("subscription.push_provider", sub3.id) == before3
    # with a ref, the un-cancel IS pushed
    await billing_svc.cancel_subscription(
        db, t3, sub3, at_period_end=True, actor=_actor(user))
    sub3.external_ref = "mock-ref-3"
    await db.flush()
    await billing_svc.reactivate_subscription(db, t3, sub3, actor=_actor(user))
    assert await _topic_count("subscription.push_provider", sub3.id) == before3 + 1
    with pytest.raises(AppError) as e409b:
        await billing_svc.cancel_subscription(
            db, tenant, sub, at_period_end=False, actor=_actor(user))
    assert e409b.value.status_code in (404, 409)


@pytest.mark.asyncio
async def test_gap_window_change_prices_seats_off_own_plan(db):
    """R348 (kills the R347-deferred gap cluster): a change landing AFTER the
    period elapsed but before the close (the R131[5]/R135 gap) must price the
    OLD seat side off the subscription's OWN plan price — the flipped-dim
    mutants pick another plan's included/overage and the seat net silently
    shifts. 4 live students, own plan (included 2, seat 500) → new plan
    (included 0, seat 300): old overage (4-2)×500=1000, new (4-0)×300=1200,
    net exactly +200 at full-window factor. (The gap-entry >= instant itself
    is a sub-µs race — documented.)"""
    from datetime import timedelta

    from app.models.organization import MemberStatus, Organization, OrgMember, OrgRole, OrgStatus

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    org = Organization(name=f"Gap {ULID()}", slug=f"gap-{str(ULID()).lower()}",
                       status=OrgStatus.ACTIVE, tenant_id=tenant.id, created_by=user.id)
    db.add(org)
    await db.flush()
    for _ in range(4):
        stu = await _mk_user(db)
        db.add(OrgMember(org_id=org.id, user_id=stu.id,
                         role=OrgRole.STUDENT, status=MemberStatus.ACTIVE))
    await db.flush()

    ka = await _seed_plan(db, user, f"r348a-{str(ULID()).lower()[:8]}",
                          amount=10000, included=2, seat_price=500)
    kb = await _seed_plan(db, user, f"r348b-{str(ULID()).lower()[:8]}",
                          amount=10000, included=0, seat_price=300)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key=ka, interval="month", seats=0,
        provider="manual", actor=_actor(user))
    # force the gap: the period elapsed an hour ago, close not yet run
    sub.current_period_start = billing_svc._now() - timedelta(days=30, hours=1)
    sub.current_period_end = billing_svc._now() - timedelta(hours=1)
    await db.flush()

    res = await billing_svc.change_plan(
        db, tenant, sub, plan_key=kb, seats=None, proration_mode="immediate",
        actor=_actor(user))
    # equal plan fee → plan-fee net 0; the whole net is the seat repricing,
    # computed against the OWN plan's gap price. Nominal +200 at factor 1;
    # the hour already elapsed shaves a sub-day fraction (observed ~193).
    # The mutant (other plan's dims: old=(4-0)×300 == new) nets ~0 — assert
    # the own-plan magnitude band.
    assert 150 <= res["proration"]["seat_proration_minor"] <= 200, res["proration"]


@pytest.mark.asyncio
async def test_payment_finalize_void_boundary_family(db):
    """R349 (mutation survivors): the invoice money-motion edges —
    finalize: double-finalize 409; a ZERO-due invoice auto-pays on finalize.
    record_payment: paying a draft/void invoice 409; duplicate
    (external_ref, method) 409 while the same ref under ANOTHER method is
    fine; a PARTIAL payment keeps the invoice open; completing it flips paid
    and reactivates a PAST_DUE tenant; require_mutable is a 409.
    void: voiding a PAID invoice 409 (credit note instead); double-void 409;
    a partly-paid open invoice's collected cash returns to the credit
    balance on void (R123[H4])."""
    from app.controlplane.models.credit import TenantCreditBalance

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)

    def _inv(due):
        return Invoice(tenant_id=tenant.id, currency="USD", status="draft",
                       subtotal_minor=due, total_minor=due, amount_due_minor=due)

    # zero-due draft → finalize auto-pays; second finalize 409
    z = _inv(0)
    db.add(z)
    await db.flush()
    z = await billing_svc.finalize_invoice(db, z, actor=_actor(user))
    assert z.status == "paid" and z.paid_at is not None and z.number
    with pytest.raises(AppError) as e_fin:
        await billing_svc.finalize_invoice(db, z, actor=_actor(user))
    assert e_fin.value.code == "INVOICE_NOT_DRAFT" and e_fin.value.status_code == 409

    # payments: draft invoice not payable; require_mutable 409
    inv = _inv(10000)
    db.add(inv)
    await db.flush()
    with pytest.raises(AppError) as e_pay0:
        await billing_svc.record_payment(
            db, inv, amount_minor=1000, method="manual_bank_transfer",
            external_ref=None, reference_note=None, received_at=None,
            actor=_actor(user))
    assert e_pay0.value.code == "INVOICE_NOT_OPEN" and e_pay0.value.status_code == 409
    inv = await billing_svc.finalize_invoice(db, inv, actor=_actor(user))
    assert inv.status == "open"

    # partial payment keeps it open
    await billing_svc.record_payment(
        db, inv, amount_minor=4000, method="manual_bank_transfer",
        external_ref="WIRE-1", reference_note=None, received_at=None,
        actor=_actor(user))
    await db.refresh(inv)
    assert inv.status == "open" and inv.paid_at is None

    # duplicate (ref, method) 409; same ref under another method is FINE
    with pytest.raises(AppError) as e_dup:
        await billing_svc.record_payment(
            db, inv, amount_minor=1000, method="manual_bank_transfer",
            external_ref="WIRE-1", reference_note=None, received_at=None,
            actor=_actor(user))
    assert e_dup.value.code == "PAYMENT_INVALID" and e_dup.value.status_code == 409
    await billing_svc.record_payment(
        db, inv, amount_minor=1000, method="other",
        external_ref="WIRE-1", reference_note=None, received_at=None,
        actor=_actor(user))

    # completing payment flips paid AND reactivates a past_due tenant
    from app.controlplane.services.tenants import transition_status

    await transition_status(db, tenant, TenantStatus.PAST_DUE,
                            actor=_actor(user), reason="dunning")
    await billing_svc.record_payment(
        db, inv, amount_minor=5000, method="manual_bank_transfer",
        external_ref="WIRE-2", reference_note=None, received_at=None,
        actor=_actor(user))
    await db.refresh(inv)
    assert inv.status == "paid" and inv.paid_at is not None
    await db.refresh(tenant)
    assert tenant.status == TenantStatus.ACTIVE

    # voiding the PAID invoice → 409 (credit note territory)
    with pytest.raises(AppError) as e_vp:
        await billing_svc.void_invoice(db, inv, reason="nope", actor=_actor(user))
    assert e_vp.value.status_code == 409

    # a partly-paid OPEN invoice: void returns collected cash to credit
    inv2 = _inv(8000)
    db.add(inv2)
    await db.flush()
    inv2 = await billing_svc.finalize_invoice(db, inv2, actor=_actor(user))
    await billing_svc.record_payment(
        db, inv2, amount_minor=3000, method="manual_bank_transfer",
        external_ref="WIRE-3", reference_note=None, received_at=None,
        actor=_actor(user))
    bal_before = (
        await db.execute(
            select(TenantCreditBalance.balance_minor).where(
                TenantCreditBalance.tenant_id == tenant.id,
                TenantCreditBalance.currency == "USD"))
    ).scalar_one_or_none() or 0
    inv2 = await billing_svc.void_invoice(db, inv2, reason="mistake", actor=_actor(user))
    assert inv2.status == "void"
    bal_after = (
        await db.execute(
            select(TenantCreditBalance.balance_minor).where(
                TenantCreditBalance.tenant_id == tenant.id,
                TenantCreditBalance.currency == "USD"))
    ).scalar_one()
    assert bal_after - bal_before == 3000        # collected cash → credit
    with pytest.raises(AppError) as e_vv:         # double void 409
        await billing_svc.void_invoice(db, inv2, reason="again", actor=_actor(user))
    assert e_vv.value.status_code == 409

    # invoice numbers are CONSECUTIVE (no sequence skips), require_mutable is
    # a 409, and a payment recorded without received_at gets stamped now
    # (never NULL). The duplicate-payment pre-check limit(1) mutant is
    # constraint-equivalent (uq_cp_payment_external) — documented.
    a, b = _inv(100), _inv(100)
    db.add_all([a, b])
    await db.flush()
    a = await billing_svc.finalize_invoice(db, a, actor=_actor(user))
    b = await billing_svc.finalize_invoice(db, b, actor=_actor(user))
    assert int(b.number.rsplit("-", 1)[1]) - int(a.number.rsplit("-", 1)[1]) == 1
    with pytest.raises(AppError) as e_mut:
        billing_svc.require_mutable(a)
    assert e_mut.value.code == "INVOICE_FINALIZED" and e_mut.value.status_code == 409
    pay = await billing_svc.record_payment(
        db, a, amount_minor=50, method="other", external_ref=None,
        reference_note=None, received_at=None, actor=_actor(user))
    assert pay.received_at is not None


@pytest.mark.asyncio
async def test_void_scoping_usage_purchases_and_later_locked_decoys(db):
    """R349b (void_invoice mutation survivors): void's write-set is scoped to
    THE voided invoice — (1) another invoice's usage lines stay invoiced;
    (2) a purchase attached to ANOTHER invoice keeps its invoice link;
    (3) the later-locked rewind guard looks at THIS subscription's periods —
    a decoy sub's later locked period must not suppress the rewind, and this
    sub's own later locked period must. (The credit-refund gate's falsy
    short-circuits and the deep fold-restore internals — watermark ordering,
    axis Nones — are documented deferrals: they encode the R129/133/135
    stacked-change semantics and need those rounds' repro shapes.)"""
    from datetime import timedelta as _td
    from decimal import Decimal

    from app.controlplane.models.marketplace import MarketplacePurchase
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent

    user = await _mk_user(db)
    a = _actor(user)
    tenant = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0,
        provider="manual", actor=a)
    # decoy tenant+sub with a later LOCKED period
    t2 = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
    sub2, _ = await billing_svc.start_subscription(
        db, t2, plan_key="school", interval="month", seats=0,
        provider="manual", actor=a)
    inv2 = await _force_close(db, sub2)          # decoy: closed+invoiced period

    def _usage_line(inv, tenant_id):
        eid = str(ULID())
        db.add(UsageEvent(id=eid, tenant_id=tenant_id, org_id=str(ULID()),
                          usage_type="image_generation", quantity=1, unit="images",
                          occurred_at=billing_svc._now(), source="manual"))
        line = InvoiceLine(invoice_id=inv.id, line_type="usage", description="u",
                           quantity=1, unit_amount_minor=100, amount_minor=100)
        db.add(line)
        return eid, line

    inv = await _force_close(db, sub)
    assert inv is not None
    eid1, line1 = _usage_line(inv, tenant.id)
    eid2, line2 = _usage_line(inv2, t2.id)
    await db.flush()

    def _rated(eid, tenant_id, line):
        return RatedUsage(usage_event_id=eid, tenant_id=tenant_id,
                          org_id=str(ULID()), usage_type="image_generation",
                          quantity=1, cost_rate_snapshot={}, internal_cost_minor=0,
                          internal_cost_currency="USD", sell_rate_snapshot={},
                          billable_amount_minor=100, billable_amount_exact=Decimal(100),
                          billable_currency="USD", status="invoiced",
                          rated_at=billing_svc._now(), invoice_line_id=line.id)

    r1, r2 = _rated(eid1, tenant.id, line1), _rated(eid2, t2.id, line2)
    db.add_all([r1, r2])
    # a purchase attached to the OTHER invoice
    from app.controlplane.models.marketplace import MarketplaceListing

    lst = MarketplaceListing(product_type="skill_pack", product_id=str(ULID()),
                             seller_org_id=str(ULID()), seller_tenant_id=str(ULID()),
                             offer_type="paid", price_minor=100, currency="USD",
                             platform_commission_pct=Decimal("20"), status="active",
                             created_by=user.id)
    db.add(lst)
    await db.flush()
    other_purchase = MarketplacePurchase(
        listing_id=lst.id, buyer_tenant_id=t2.id, buyer_org_id=str(ULID()),
        purchaser_user_id=user.id, status="paid", amount_minor=100,
        currency="USD", platform_fee_minor=20, seller_share_minor=80,
        partner_share_minor=0, economics_snapshot={}, invoice_id=inv2.id,
        payment_method="invoice")
    db.add(other_purchase)
    await db.flush()

    voided = await billing_svc.void_invoice(db, inv, reason="scope", actor=a)
    assert voided.status == "void"
    await db.refresh(r1)
    await db.refresh(r2)
    assert r1.status == "rated" and r1.invoice_line_id is None      # unbound
    assert r2.status == "invoiced" and r2.invoice_line_id == line2.id  # untouched
    await db.refresh(other_purchase)
    assert other_purchase.invoice_id == inv2.id                     # link kept

    # rewind DID happen for this sub (decoy's later period didn't block it):
    # the voided invoice's period is open again
    period = await db.get(BillingPeriod, voided.billing_period_id)
    assert period.status == "open"

    # now give THIS sub a later locked period → voiding the OLDER invoice
    # must NOT rewind (its period stays closed/invoiced)
    period.status = "invoiced"
    sub.current_period_start = sub.current_period_end
    sub.current_period_end = sub.current_period_end + _td(days=30)
    db.add(BillingPeriod(tenant_id=tenant.id, subscription_id=sub.id,
                         status="open",
                         period_start=sub.current_period_start,
                         period_end=sub.current_period_end))
    await db.flush()
    inv_b = Invoice(tenant_id=tenant.id, currency="USD", status="open",
                    subtotal_minor=0, total_minor=0, amount_due_minor=0,
                    billing_period_id=period.id, finalized_at=billing_svc._now())
    db.add(inv_b)
    later = await _force_close(db, sub)          # later period → closed/invoiced
    assert later is not None
    await db.flush()
    voided_b = await billing_svc.void_invoice(db, inv_b, reason="older", actor=a)
    assert voided_b.status == "void"
    await db.refresh(period)
    assert period.status == "invoiced"           # rewind suppressed (own later lock)


def test_webhook_pure_boundaries():
    """R354 (mutation survivors, pure units): (1) an event at EXACTLY the
    HWM instant is NOT stale (equal-time redelivery still applies) and does
    not re-advance the HWM (idempotent); (2) _subscription_ref tolerates a
    NULL parent / NULL subscription_details (basil-shape payloads) without
    crashing and reads both API shapes."""
    from types import SimpleNamespace

    now = datetime.now(UTC)
    sub = SimpleNamespace(last_billing_event_at=now)
    same = SimpleNamespace(occurred_at=now)
    older = SimpleNamespace(occurred_at=now - timedelta(seconds=1))
    newer = SimpleNamespace(occurred_at=now + timedelta(seconds=1))
    assert billing_svc._is_stale_billing_event(sub, same) is False   # == not stale
    assert billing_svc._is_stale_billing_event(sub, older) is True
    assert billing_svc._is_stale_billing_event(sub, newer) is False
    billing_svc._advance_billing_event_hwm(sub, same)
    assert sub.last_billing_event_at == now                          # == no advance
    billing_svc._advance_billing_event_hwm(sub, newer)
    assert sub.last_billing_event_at == newer.occurred_at

    assert billing_svc._subscription_ref({}) is None
    assert billing_svc._subscription_ref({"parent": None}) is None
    assert billing_svc._subscription_ref({"parent": {"subscription_details": None}}) is None
    assert billing_svc._subscription_ref({"subscription": "sub_1"}) == "sub_1"
    assert billing_svc._subscription_ref(
        {"parent": {"subscription_details": {"subscription": "sub_2"}}}) == "sub_2"
    assert billing_svc._subscription_ref(
        {"parent": {"subscription_details": {"subscription": {"id": "sub_3"}}}}) == "sub_3"


@pytest.mark.asyncio
async def test_webhook_provider_gate_and_checkout_suspension_rescue(db):
    """R354: (1) process_webhook for 'manual' and unknown providers is a
    uniform 401 (no oracle); (2) checkout activation rescues EXACTLY the
    trial-expiry suspension — an ABUSE-suspended tenant completing checkout
    stays suspended (payment is never self-service un-suspension), a
    'trial expired' suspension reactivates."""
    with pytest.raises(AppError) as e_m:
        await billing_svc.process_webhook(db, "manual", {}, b"{}")
    assert e_m.value.code == "WEBHOOK_SIGNATURE_INVALID" and e_m.value.status_code == 401
    with pytest.raises(AppError) as e_u:
        await billing_svc.process_webhook(db, "carrier_pigeon", {}, b"{}")
    assert e_u.value.status_code == 401

    user = await _mk_user(db)
    ka = await _seed_plan(db, user, f"r354-{str(ULID()).lower()[:8]}",
                          amount=5000, included=0, seat_price=None)

    async def _suspended_tenant(reason):
        t = await _mk_tenant(db, user, status=TenantStatus.ACTIVE)
        from app.controlplane.services.tenants import transition_status
        await transition_status(db, t, TenantStatus.SUSPENDED,
                                actor=_actor(user), reason=reason)
        return t

    t_abuse = await _suspended_tenant("terms violation")
    t_trial = await _suspended_tenant("trial expired")
    for t, ref in ((t_abuse, f"cs-a-{ULID()}"), (t_trial, f"cs-t-{ULID()}")):
        await billing_svc.activate_subscription_from_checkout(
            db, t, plan_key=ka, interval="month", seats=0,
            provider="mock", external_customer_ref=None, external_ref=ref)
    await db.refresh(t_abuse)
    await db.refresh(t_trial)
    assert t_abuse.status == TenantStatus.SUSPENDED    # payment ≠ un-suspend
    assert t_trial.status == TenantStatus.ACTIVE       # cron's suspension rescued

    # duplicate-checkout orphan handling: a REDELIVERY (same external_ref)
    # must NOT cancel the live provider subscription; a genuinely different
    # second checkout cancels the orphan exactly once (R64[17])
    import app.controlplane.services.billing_providers as bp_mod

    cancels: list = []
    real_get = bp_mod.get_billing_provider

    def spying_get(provider):
        adapter = real_get(provider)
        if adapter is not None:
            class Spy:
                def __getattr__(self, name):
                    attr = getattr(adapter, name)
                    if name == "cancel_subscription":
                        async def rec(*a, **kw):
                            cancels.append((a, kw))
                            return None
                        return rec
                    return attr
            return Spy()
        return adapter

    import unittest.mock as _mock

    with _mock.patch.object(bp_mod, "get_billing_provider", spying_get):
        sub_live = await billing_svc.get_live_subscription(db, t_trial.id)
        # redelivery: SAME ref as the live sub → no cancel
        await billing_svc.activate_subscription_from_checkout(
            db, t_trial, plan_key=ka, interval="month", seats=0,
            provider="mock", external_customer_ref=None,
            external_ref=sub_live.external_ref)
        assert cancels == []
        # different ref (double-click second session) → orphan cancelled once
        await billing_svc.activate_subscription_from_checkout(
            db, t_trial, plan_key=ka, interval="month", seats=0,
            provider="mock", external_customer_ref=None,
            external_ref=f"cs-orphan-{ULID()}")
        assert len(cancels) == 1


@pytest.mark.asyncio
async def test_webhook_applier_dunning_and_checkout_edges(db):
    """R356 (mutation survivors in _apply_webhook_event): (1) invoice.paid
    recovers EXACTLY a PAST_DUE tenant — a SUSPENDED tenant is never
    self-service reactivated by a payment event; (2) payment_failed marks
    EXACTLY an ACTIVE tenant past_due — a suspended one stays; (3) a checkout
    with an EMPTY seats metadata activates with 0 seats (the or→and mutant
    int('')-crashes); (4) a subscription checkout without a subscription
    field falls back to the session id as the external ref."""
    from app.controlplane.services.billing_providers.mock import sign_mock_event

    user = await _mk_user(db)

    async def _send(payload):
        raw, sig = sign_mock_event(payload)
        return await billing_svc.process_webhook(
            db, "mock", {"x-mock-signature": sig}, raw)

    def _checkout(tenant, *, seats, subscription="auto", session=None):
        data = {
            "id": session or f"mock_sess_{ULID()}",
            "customer": f"mock_cus_{tenant.id}",
            "metadata": {"tenant_id": tenant.id, "kind": "subscription",
                         "plan_key": "school", "interval": "month",
                         "seats": seats},
        }
        if subscription == "auto":
            data["subscription"] = f"mock_sub_{ULID()}"
        return {"id": f"mevt_{ULID()}", "type": "checkout.completed", "data": data}

    # (3) empty seats string → 0 seats, activated
    t_empty = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    r = await _send(_checkout(t_empty, seats=""))
    assert r["status"] == "processed"
    sub_e = await billing_svc.get_live_subscription(db, t_empty.id)
    assert sub_e is not None and sub_e.seat_quantity == 0

    # (4) no subscription field → session id becomes the external ref
    t_nosub = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    session_id = f"mock_sess_{ULID()}"
    r = await _send(_checkout(t_nosub, seats="0", subscription=None,
                              session=session_id))
    assert r["status"] == "processed"
    sub_n = await billing_svc.get_live_subscription(db, t_nosub.id)
    assert sub_n is not None and sub_n.external_ref == session_id

    # (1)+(2) dunning transitions keyed to the sub's external ref
    async def _pay_event(sub, etype):
        return await _send({
            "id": f"mevt_{ULID()}", "type": etype,
            "data": {"id": f"in_{ULID()}", "subscription": sub.external_ref}})

    from app.controlplane.services.tenants import transition_status

    # ACTIVE + payment_failed → PAST_DUE
    t1 = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    await _send(_checkout(t1, seats="0"))
    sub1 = await billing_svc.get_live_subscription(db, t1.id)
    await db.refresh(t1)
    assert t1.status == TenantStatus.ACTIVE
    await _pay_event(sub1, "invoice.payment_failed")
    await db.refresh(t1)
    assert t1.status == TenantStatus.PAST_DUE
    # PAST_DUE + invoice.paid → ACTIVE again
    await _pay_event(sub1, "invoice.paid")
    await db.refresh(t1)
    assert t1.status == TenantStatus.ACTIVE
    # SUSPENDED: neither event moves it (no self-service un-suspension,
    # and payment_failed must not stack a suspension into past_due)
    await transition_status(db, t1, TenantStatus.SUSPENDED,
                            actor=_actor(user), reason="abuse")
    r_paid = await _pay_event(sub1, "invoice.paid")
    await db.refresh(t1)
    assert t1.status == TenantStatus.SUSPENDED
    r_fail = await _pay_event(sub1, "invoice.payment_failed")
    await db.refresh(t1)
    assert t1.status == TenantStatus.SUSPENDED
    # both events PROCESS cleanly (the flipped gates attempt an illegal
    # matrix transition and dead-letter the webhook instead)
    assert r_paid["status"] == "processed" and r_fail["status"] == "processed"

    # a TRIAL tenant is not dunned into past_due by a stray payment_failed
    t_trial2 = await _mk_tenant(db, user, status=TenantStatus.TRIAL)
    sub_t, _ = await billing_svc.start_subscription(
        db, t_trial2, plan_key="school", interval="month", seats=0,
        provider="manual", actor=_actor(user))
    sub_t.provider = "mock"
    sub_t.external_ref = f"mock_sub_{ULID()}"
    sub_t.status = "trial"
    t_trial2.status = TenantStatus.TRIAL     # start_subscription activated it
    await db.flush()
    r_trial = await _pay_event(sub_t, "invoice.payment_failed")
    await db.refresh(t_trial2)
    assert t_trial2.status == TenantStatus.TRIAL
    assert r_trial["status"] == "processed"

    # a purchase-kind checkout marks the purchase PAID (the flipped kind
    # matcher routes it to the subscription handler instead)
    from decimal import Decimal as PDec

    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase

    lst = MarketplaceListing(product_type="skill_pack", product_id=str(ULID()),
                             seller_org_id=str(ULID()), seller_tenant_id=str(ULID()),
                             offer_type="paid", price_minor=100, currency="USD",
                             platform_commission_pct=PDec("20"), status="active",
                             created_by=user.id)
    db.add(lst)
    await db.flush()
    pur = MarketplacePurchase(
        listing_id=lst.id, buyer_tenant_id=t1.id, buyer_org_id=str(ULID()),
        purchaser_user_id=user.id, status="pending", amount_minor=100,
        currency="USD", platform_fee_minor=20, seller_share_minor=80,
        partner_share_minor=0, economics_snapshot={"seller_org_id": None},
        payment_method="checkout")
    db.add(pur)
    await db.flush()
    r = await _send({
        "id": f"mevt_{ULID()}", "type": "checkout.completed",
        "data": {"id": f"mock_sess_{ULID()}",
                 "metadata": {"tenant_id": t1.id, "kind": "purchase",
                              "purchase_id": pur.id}}})
    assert r["status"] == "processed"
    await db.refresh(pur)
    assert pur.status == "paid"
