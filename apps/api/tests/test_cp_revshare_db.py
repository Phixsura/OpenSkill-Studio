"""P7 DB tests: revenue-share accrual, rule versioning immutability,
statements, cross-partner isolation."""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.billing import Invoice
from app.controlplane.models.partner import (
    Partner,
    PartnerMember,
    RevenueShareEntry,
    RevenueShareRule,
)
from app.controlplane.models.tenant import TenantAccount, TenantStatus
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
        email=f"cp7-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP7",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_partner(db, user) -> Partner:
    partner = Partner(
        name=f"P {ULID()}",
        slug=f"p-{str(ULID()).lower()}",
        partner_type="reseller",
        currency="USD",
        created_by=user.id,
    )
    db.add(partner)
    await db.flush()
    db.add(PartnerMember(partner_id=partner.id, user_id=user.id, role="admin", created_by=user.id))
    await db.flush()
    return partner


async def _mk_tenant(db, user, partner=None) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"T {ULID()}",
        slug=f"t7-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
        partner_id=partner.id if partner else None,
    )


async def _mk_rule(db, user, partner, *, rate="10", version=1, **dims) -> RevenueShareRule:
    rule = RevenueShareRule(
        beneficiary_type="partner",
        partner_id=partner.id,
        revenue_type=dims.pop("revenue_type", "all"),
        rule_type=dims.pop("rule_type", "percentage_of_gross_revenue"),
        rate=Decimal(rate),
        version=version,
        effective_from=datetime.now(UTC) - timedelta(days=30),
        created_by=user.id,
        **dims,
    )
    db.add(rule)
    await db.flush()
    return await revshare_svc.activate_rule(db, rule, actor=Actor(user_id=user.id, type="platform"))


async def _mk_invoice(db, tenant, subtotal=100000) -> Invoice:
    invoice = Invoice(
        tenant_id=tenant.id,
        currency="USD",
        status="open",
        subtotal_minor=subtotal,
        total_minor=subtotal,
        amount_due_minor=subtotal,
        finalized_at=datetime.now(UTC),
    )
    db.add(invoice)
    await db.flush()
    return invoice


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── Pure logic ───────────────────────────────────────────────


def test_specificity_scoring():
    def mk(**kw):
        return RevenueShareRule(
            beneficiary_type="partner",
            revenue_type="all",
            rule_type="percentage_of_gross_revenue",
            version=1,
            effective_from=datetime.now(UTC),
            **kw,
        )

    ctx = dict(tenant_id="t1", plan_id="p1", listing_id=None, country="CN")
    assert revshare_svc.rule_specificity(mk(), **ctx) == 0  # global
    assert revshare_svc.rule_specificity(mk(tenant_id="t1"), **ctx) == 8
    assert revshare_svc.rule_specificity(mk(tenant_id="t2"), **ctx) is None
    assert revshare_svc.rule_specificity(mk(plan_id="p1", country="CN"), **ctx) == 5
    assert revshare_svc.rule_specificity(mk(tenant_id="t1", plan_id="p1"), **ctx) == 12


def test_compute_share_matrix():
    f = revshare_svc.compute_share_minor
    assert (
        f("percentage_of_gross_revenue", rate=Decimal("10"), amount_minor=None, base_minor=100000)
        == 10000
    )
    assert (
        f("percentage_of_margin", rate=Decimal("25"), amount_minor=None, base_minor=40000) == 10000
    )
    assert (
        f("fixed_amount_per_seat", rate=None, amount_minor=200, base_minor=0, units=Decimal(12))
        == 2400
    )
    assert f("fixed_amount_per_unit", rate=None, amount_minor=5000, base_minor=0) == 5000


# ── Accrual ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_invoice_accrual_and_replay_idempotency(db):
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="15")
    invoice = await _mk_invoice(db, tenant, subtotal=200000)  # $2000
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry is not None
    assert entry.share_amount_minor == 30000  # 15%
    assert Decimal(entry.rule_snapshot["rate"]) == Decimal("15")
    # Replay (outbox redelivery) → no duplicate
    again = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert again is None
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry).where(RevenueShareEntry.source_id == invoice.id)
            )
        )
        .scalars()
        .all()
    )
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_unattributed_tenant_no_accrual(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, partner=None)
    invoice = await _mk_invoice(db, tenant)
    assert await revshare_svc.accrue_for_invoice(db, invoice.id) is None


@pytest.mark.asyncio
async def test_terminated_partner_stops_accruing(db):
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner)
    partner.status = "terminated"
    await db.flush()
    invoice = await _mk_invoice(db, tenant)
    assert await revshare_svc.accrue_for_invoice(db, invoice.id) is None


@pytest.mark.asyncio
async def test_suspended_partner_still_accrues(db):
    """R35/C28: SUSPENDED is a temporary payout hold, not a stop. The revenue
    is still earned, and invoice.finalized fires exactly once — dropping the
    accrual here would lose it permanently. Only TERMINATED stops accrual."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    partner.status = "suspended"
    await db.flush()
    invoice = await _mk_invoice(db, tenant, subtotal=100000)
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry is not None and entry.share_amount_minor == 10000


@pytest.mark.asyncio
async def test_missing_fx_raises_not_silently_drops(db):
    """R35/C24: a missing FX rate for a cross-currency accrual must RAISE (so
    the outbox retries / dead-letters), not return None (which the worker
    marks done → the accrual is lost forever)."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)  # partner currency USD
    partner.currency = "EUR"
    tenant = await _mk_tenant(db, user, partner)
    tenant.currency = "USD"
    await _mk_rule(db, user, partner, rate="10")
    await db.flush()
    invoice = await _mk_invoice(db, tenant, subtotal=100000)  # USD invoice, no USD→EUR rate
    with pytest.raises(AppError) as exc:
        await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert exc.value.code == "REVSHARE_FX_MISSING"


@pytest.mark.asyncio
async def test_rule_versioning_never_rewrites_history(db):
    """Issue §23 acceptance: activating v2 leaves v1-based entries intact."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10", version=1)
    invoice1 = await _mk_invoice(db, tenant, subtotal=100000)
    entry1 = await revshare_svc.accrue_for_invoice(db, invoice1.id)
    assert entry1.share_amount_minor == 10000
    frozen_snapshot = dict(entry1.rule_snapshot)
    # Activate v2 at double the rate
    await _mk_rule(db, user, partner, rate="20", version=2)
    # Replay the old invoice — natural key blocks re-accrual
    assert await revshare_svc.accrue_for_invoice(db, invoice1.id) is None
    await db.refresh(entry1)
    assert entry1.share_amount_minor == 10000
    assert dict(entry1.rule_snapshot) == frozen_snapshot
    # New invoice accrues at v2
    invoice2 = await _mk_invoice(db, tenant, subtotal=100000)
    entry2 = await revshare_svc.accrue_for_invoice(db, invoice2.id)
    assert entry2.share_amount_minor == 20000
    assert entry2.rule_snapshot["version"] == 2


@pytest.mark.asyncio
async def test_specific_rule_beats_general(db):
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10", version=1)  # global
    await _mk_rule(db, user, partner, rate="25", version=1, tenant_id=tenant.id)
    invoice = await _mk_invoice(db, tenant, subtotal=100000)
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry.share_amount_minor == 25000  # tenant-specific won


# ── Statements ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_statement_lifecycle_and_totals(db):
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    period = datetime.now(UTC).strftime("%Y-%m")
    inv1 = await _mk_invoice(db, tenant, subtotal=100000)
    inv2 = await _mk_invoice(db, tenant, subtotal=50000)
    await revshare_svc.accrue_for_invoice(db, inv1.id)
    await revshare_svc.accrue_for_invoice(db, inv2.id)
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=period,
        actor=_actor(user),
    )
    assert statement.gross_revenue_minor == 150000
    assert statement.share_total_minor == 15000
    assert statement.net_amount_minor == 15000
    # Manual adjustment
    statement = await revshare_svc.adjust_statement(
        db, statement, amount_minor=-1500, reason="chargeback share", actor=_actor(user)
    )
    assert statement.net_amount_minor == 13500
    # Regeneration in draft keeps totals reproducible (manual adj entry persists)
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=period,
        actor=_actor(user),
    )
    assert statement.share_total_minor == 15000 - 1500  # manual entry now in-period
    # finalize → approve → mark-paid
    statement = await revshare_svc.transition_statement(
        db, statement, "finalize", actor=_actor(user)
    )
    assert statement.status == "finalized"
    with pytest.raises(AppError):  # illegal jump
        await revshare_svc.transition_statement(
            db, statement, "mark-paid", actor=_actor(user), external_payment_ref="W-1"
        )
    statement = await revshare_svc.transition_statement(
        db, statement, "approve", actor=_actor(user)
    )
    statement = await revshare_svc.transition_statement(
        db, statement, "mark-paid", actor=_actor(user), external_payment_ref="WIRE-42"
    )
    assert statement.status == "paid_externally"
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry).where(RevenueShareEntry.statement_id == statement.id)
            )
        )
        .scalars()
        .all()
    )
    assert all(e.status == "settled" for e in entries)
    # Post-finalize generation for the same period → 409
    with pytest.raises(AppError) as exc:
        await revshare_svc.generate_statement(
            db,
            beneficiary_type="partner",
            partner_id=partner.id,
            beneficiary_org_id=None,
            period=period,
            actor=_actor(user),
        )
    assert exc.value.code == "STATEMENT_STATUS_CONFLICT"


@pytest.mark.asyncio
async def test_late_adjustment_lands_in_next_opening(db):
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    # A stray adjusted entry from LAST month, never bound to a statement
    last_month = (datetime.now(UTC).replace(day=1) - timedelta(days=1)).strftime("%Y-%m")
    db.add(
        RevenueShareEntry(
            beneficiary_type="partner",
            partner_id=partner.id,
            source_type="marketplace_purchase",
            source_id=str(ULID()),
            rule_snapshot={"late": True},
            revenue_base_minor=-10000,
            share_amount_minor=-1000,
            currency="USD",
            period=last_month,
            status="adjusted",
        )
    )
    await db.flush()
    period = datetime.now(UTC).strftime("%Y-%m")
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=period,
        actor=_actor(user),
    )
    assert statement.opening_adjustments_minor == -1000
    assert statement.net_amount_minor == -1000


# ── Cross-partner isolation ──────────────────────────────────


@pytest.mark.asyncio
async def test_cross_partner_uniform_404(db):
    from app.controlplane.api.partners import require_partner_member

    user_a = await _mk_user(db)
    user_b = await _mk_user(db)
    partner_a = await _mk_partner(db, user_a)
    partner_b = await _mk_partner(db, user_b)
    # A's member reads B → uniform 404 (existence hidden)
    with pytest.raises(AppError) as exc:
        await require_partner_member(db, partner_b.id, user_a)
    assert exc.value.code == "PARTNER_NOT_FOUND" and exc.value.status_code == 404
    # Nonexistent partner → same 404
    with pytest.raises(AppError) as exc2:
        await require_partner_member(db, str(ULID()), user_a)
    assert exc2.value.code == "PARTNER_NOT_FOUND"
    # Member (non-admin) hits admin-only surface → 403
    member_user = await _mk_user(db)
    db.add(
        PartnerMember(
            partner_id=partner_a.id,
            user_id=member_user.id,
            role="member",
            created_by=user_a.id,
        )
    )
    await db.flush()
    with pytest.raises(AppError) as exc3:
        await require_partner_member(db, partner_a.id, member_user, "admin")
    assert exc3.value.code == "PARTNER_FORBIDDEN"
