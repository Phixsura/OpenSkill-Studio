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
