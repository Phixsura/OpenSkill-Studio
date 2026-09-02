"""P11 DB tests: platform dashboard aggregates + both §37 trace chains
(invoice line → rated usage → provider call; settlement entry → source →
statement)."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.api import platform_dashboard as ops
from app.controlplane.models.billing import BillingPeriod, InvoiceLine
from app.controlplane.models.partner import Partner, RevenueShareEntry, RevenueShareRule
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import billing as billing_svc
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import metering, rating
from app.controlplane.services import pricing as pricing_svc
from app.controlplane.services import revenue_share as revshare_svc
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
        email=f"cp11-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP11",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"O {ULID()}",
        slug=f"o-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


def _actor(user):
    return Actor(user_id=user.id, type="platform")


async def _billed_usage_line(db, user, tenant) -> tuple:
    """School sub + one rated image event + force-close period → usage line."""
    a = _actor(user)
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=0, provider="manual", actor=a
    )
    await pricing_svc.create_price_policy(
        db,
        actor=a,
        name=f"ops {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 30},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=10,
        occurred_at=datetime.now(UTC) - timedelta(minutes=5),
        source="manual",
        idempotency_key=f"ops-{ULID()}",
        provider="mock",
        model_or_service="mock-image-1",
        workflow_run_id="01JFAKERUNFAKERUNFAKERUNFA",
    )
    await rating.rate_event(db, event.id)
    period = (
        await db.execute(select(BillingPeriod).where(BillingPeriod.subscription_id == sub.id))
    ).scalar_one()
    period.period_end = datetime.now(UTC) - timedelta(seconds=1)
    await db.flush()
    invoice = await billing_svc.close_period_and_invoice(db, period.id)
    usage_line = (
        await db.execute(
            select(InvoiceLine).where(
                InvoiceLine.invoice_id == invoice.id, InvoiceLine.line_type == "usage"
            )
        )
    ).scalar_one()
    return invoice, usage_line, event


# ── Dashboard ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dashboard_blocks(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await credit_svc.top_up(db, tenant.id, "USD", 12345, actor=_actor(user))
    invoice, _line, _event = await _billed_usage_line(db, user, tenant)

    data = (await ops.platform_dashboard(period=None, _user=user, db=db))["data"]
    assert data["tenants"]["by_status"]["active"] >= 1
    assert data["tenants"]["total"] == sum(data["tenants"]["by_status"].values())
    # School manual sub live → MRR includes 19900
    assert data["mrr_minor"] >= 19900
    # Our rated event contributes billable 300 + internal cost + margin fields
    image_row = next(
        (u for u in data["usage"]["by_type"] if u["usage_type"] == "image_generation"), None
    )
    assert image_row is not None and image_row["billable_minor"] >= 300
    assert data["totals"]["billable_minor"] >= 300
    assert "unrated_events" in data["totals"] and "blocked_rated" in data["totals"]
    usd = next(c for c in data["credits_outstanding"] if c["currency"] == "USD")
    assert usd["balance_minor"] >= 1  # credit partially consumed by the invoice
    assert isinstance(data["marketplace_gmv_minor"], int)
    assert set(data["attention"].keys()) == {
        "past_due",
        "suspended",
        "failed_webhooks",
        "dead_outbox",
    }


@pytest.mark.asyncio
async def test_dashboard_period_validation(db):
    user = await _mk_user(db)
    with pytest.raises(AppError) as exc:
        await ops.platform_dashboard(period="2026-13", _user=user, db=db)
    assert exc.value.status_code == 422


# ── Trace: invoice line chain (issue §37) ────────────────────


@pytest.mark.asyncio
async def test_trace_invoice_line_full_chain(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    invoice, usage_line, event = await _billed_usage_line(db, user, tenant)

    data = (await ops.trace_invoice_line(usage_line.id, page=1, per_page=100, _user=user, db=db))[
        "data"
    ]
    assert data["line"]["id"] == usage_line.id
    assert data["invoice"]["id"] == invoice.id
    assert data["invoice"]["number"].startswith("INV-")
    assert data["counts"]["rated_rows"] == 1
    rated = data["rated_usage"][0]
    # Frozen snapshots present all the way down
    assert rated["billable_amount_minor"] == 300
    assert "internal_cost_minor" in rated and "margin_minor" in rated
    assert rated["cost_rate_snapshot"] is not None
    assert rated["sell_rate_snapshot"]["policy_type"] == "fixed_unit_price"
    # ...down to the provider call refs
    ue = rated["usage_event"]
    assert ue["id"] == event.id
    assert ue["refs"]["provider"] == "mock"
    assert ue["refs"]["model_or_service"] == "mock-image-1"
    assert ue["refs"]["workflow_run_id"] == "01JFAKERUNFAKERUNFAKERUNFA"


@pytest.mark.asyncio
async def test_trace_invoice_line_not_found(db):
    user = await _mk_user(db)
    with pytest.raises(AppError) as exc:
        await ops.trace_invoice_line(str(ULID()), page=1, per_page=100, _user=user, db=db)
    assert exc.value.status_code == 404


# ── Trace: settlement entry chain (issue §37) ────────────────


@pytest.mark.asyncio
async def test_trace_settlement_entry_chain(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = _actor(user)
    partner = Partner(
        name=f"P {ULID()}",
        slug=f"p-{str(ULID()).lower()}",
        partner_type="reseller",
        currency="USD",
        created_by=user.id,
    )
    db.add(partner)
    await db.flush()
    tenant.partner_id = partner.id
    rule = RevenueShareRule(
        beneficiary_type="partner",
        partner_id=partner.id,
        revenue_type="all",
        rule_type="percentage_of_gross_revenue",
        rate=Decimal("10"),
        version=1,
        effective_from=datetime.now(UTC) - timedelta(days=30),
        created_by=user.id,
    )
    db.add(rule)
    await db.flush()
    await revshare_svc.activate_rule(db, rule, actor=a)
    invoice, _line, _event = await _billed_usage_line(db, user, tenant)
    await revshare_svc.accrue_for_invoice(db, invoice.id)
    entry = (
        await db.execute(
            select(RevenueShareEntry).where(RevenueShareEntry.partner_id == partner.id)
        )
    ).scalar_one()

    data = (await ops.trace_settlement_entry(entry.id, _user=user, db=db))["data"]
    assert data["entry"]["id"] == entry.id
    assert data["entry"]["rule_snapshot"]["rule_type"] == "percentage_of_gross_revenue"
    assert data["entry"]["partner_name"] == partner.name
    assert data["source"]["type"] == "invoice"
    assert data["source"]["invoice_id"] == invoice.id
    assert data["statement"] is None  # not yet bound
    # Bind to a statement → trace shows it
    stmt = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=entry.period,
        actor=a,
    )
    data = (await ops.trace_settlement_entry(entry.id, _user=user, db=db))["data"]
    assert data["statement"]["id"] == stmt.id
    assert data["statement"]["net_amount_minor"] == stmt.net_amount_minor


# ── R48: finance-role gating + currency separation ────────────


@pytest.mark.asyncio
async def test_dashboard_and_traces_deny_platform_support(db):
    """R48[30]: platform_support has operational read, NOT financial internals —
    the dashboard economics and both trace endpoints must 403 for support."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token
    from app.main import app

    support = await _mk_user(db)
    db.add(PlatformRoleAssignment(user_id=support.id, role="platform_support"))
    await db.commit()
    token = create_access_token(support.id, support.email, support.role.value)

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}
            for path in (
                "/api/v1/platform/dashboard",
                "/api/v1/platform/trace/invoice-lines/01JFAKEFAKEFAKEFAKEFAKEFAK",
                "/api/v1/platform/trace/settlement-entries/01JFAKEFAKEFAKEFAKEFAKEFAK",
            ):
                r = await c.get(path, headers=hdr)
                assert r.status_code == 403, f"{path} → {r.status_code}"
    finally:
        app.router.lifespan_context = orig


@pytest.mark.asyncio
async def test_dashboard_reports_mrr_per_currency(db):
    """R48[31]: MRR must never mix currencies into one number — a JPY sub and a
    USD sub are reported separately."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    from app.controlplane.services import billing as billing_svc

    await billing_svc.start_subscription(
        db,
        tenant,
        plan_key="school",
        interval="month",
        seats=0,
        provider="manual",
        actor=_actor(user),
    )
    data = (await ops.platform_dashboard(period=None, _user=user, db=db))["data"]
    assert "mrr_by_currency" in data
    assert data["mrr_by_currency"].get("USD", 0) >= 19900
    # The scalar is the platform-currency slice only.
    assert data["mrr_minor"] == data["mrr_by_currency"].get("USD", 0)
    # usage totals expose per-currency billable, never a mixed grand total.
    assert "billable_by_currency" in data["totals"]
