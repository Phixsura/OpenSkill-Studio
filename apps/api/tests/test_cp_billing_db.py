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
