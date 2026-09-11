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
async def test_activate_rule_retires_only_same_country(db):
    """R35/C26: country is part of rule identity. Activating a v2 for one
    country must retire only that country's active rule, never collaterally
    retire another country's active rule in the same dimension set."""

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    us1 = await _mk_rule(db, user, partner, rate="10", version=1, country="US")
    gb1 = await _mk_rule(db, user, partner, rate="12", version=1, country="GB")
    assert us1.status == "active" and gb1.status == "active"
    # Activate a US v2 → retires US v1 only
    await _mk_rule(db, user, partner, rate="15", version=2, country="US")
    await db.refresh(us1)
    await db.refresh(gb1)
    assert us1.status == "retired"
    assert gb1.status == "active"  # untouched — different country


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
    assert exc.value.code == "REVSHARE_FX_MISSING" and exc.value.status_code == 409


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
    # R50[42]: regeneration must NOT double-count the manual adjustment.
    # The old unbind released the manual entry into the collectible pool, so
    # share_total absorbed it (13500) while manual_adjustments_minor still
    # carried it → net dropped to 12000. Manual entries stay bound: share_total
    # remains the accrual sum and net is reproducible across regenerations.
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=period,
        actor=_actor(user),
    )
    assert statement.share_total_minor == 15000
    assert statement.manual_adjustments_minor == -1500
    assert statement.net_amount_minor == 13500
    # Regenerating again is idempotent on totals
    statement = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=period,
        actor=_actor(user),
    )
    assert statement.net_amount_minor == 13500
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


# ── R56: currency correctness + typed base + split rebalance ──


@pytest.mark.asyncio
async def test_revenue_type_scoped_rule_accrues_on_typed_base(db):
    """R56[23]: a rule scoped to revenue_type='usage' must accrue on the usage
    lines only — not the whole subtotal (which mixes plan/seats/license)."""
    from app.controlplane.models.billing import InvoiceLine

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="30", revenue_type="usage")
    invoice = await _mk_invoice(db, tenant, subtotal=110000)
    db.add_all(
        [
            InvoiceLine(
                invoice_id=invoice.id,
                line_type="plan",
                description="plan",
                quantity=1,
                amount_minor=100000,
            ),
            InvoiceLine(
                invoice_id=invoice.id,
                line_type="usage",
                description="usage",
                quantity=1,
                amount_minor=10000,
            ),
        ]
    )
    await db.flush()
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry is not None
    # 30% of the USAGE slice (10000) = 3000 — not 30% of 110000 = 33000.
    assert entry.share_amount_minor == 3000, entry.share_amount_minor
    assert entry.revenue_base_minor == 10000


@pytest.mark.asyncio
async def test_purchase_partner_entry_converted_to_partner_currency(db):
    """R56[22]: a marketplace-purchase partner entry must be denominated in the
    PARTNER's settlement currency (statements are single-currency)."""
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)  # USD partner
    tenant = await _mk_tenant(db, user, partner)
    # Buyer paid in JPY; partner settles in USD. 1 USD = 150 JPY.
    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="JPY",
        quote_currency="USD",
        rate=Decimal("0.0066667"),
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    listing = MarketplaceListing(
        product_type="workflow_pack",
        product_id=str(ULID()),
        seller_org_id=str(ULID()),
        seller_tenant_id=str(ULID()),
        offer_type="paid",
        price_minor=150000,
        currency="JPY",
        platform_commission_pct=Decimal("20"),
        status="active",
        created_by=user.id,
    )
    db.add(listing)
    await db.flush()
    purchase = MarketplacePurchase(
        listing_id=listing.id,
        buyer_tenant_id=tenant.id,
        buyer_org_id=str(ULID()),
        purchaser_user_id=user.id,
        status="paid",
        amount_minor=150000,  # ¥150,000
        currency="JPY",
        platform_fee_minor=30000,
        seller_share_minor=120000,
        partner_share_minor=15000,  # ¥15,000
        economics_snapshot={
            "partner_id": partner.id,
            "seller_org_id": None,
        },
    )
    db.add(purchase)
    await db.flush()
    created = await revshare_svc.accrue_for_purchase(db, purchase.id)
    assert created == 1
    entry = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.source_id == purchase.id,
                RevenueShareEntry.beneficiary_type == "partner",
            )
        )
    ).scalar_one()
    # ¥15,000 (JPY minor ×1) → $100.00 → 10000 USD minor (cents).
    assert entry.currency == "USD"
    assert abs(entry.share_amount_minor - 10000) <= 2, entry.share_amount_minor


@pytest.mark.asyncio
async def test_void_invoice_reverses_accrual(db):
    """R56[24]: voiding an invoice must negate its accrued entries so the
    re-invoice doesn't double-pay the partner."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="20")
    invoice = await _mk_invoice(db, tenant, subtotal=10000)
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry is not None and entry.share_amount_minor == 2000
    reversed_n = await revshare_svc.reverse_invoice_accruals(db, invoice.id)
    assert reversed_n == 1
    entries = (
        (
            await db.execute(
                select(RevenueShareEntry).where(RevenueShareEntry.source_id == invoice.id)
            )
        )
        .scalars()
        .all()
    )
    assert sum(e.share_amount_minor for e in entries) == 0
    # Idempotent — a second reversal creates nothing.
    assert await revshare_svc.reverse_invoice_accruals(db, invoice.id) == 0


def test_seller_rule_override_rebalances_split():
    """R56[25]: a seller-specific rate override must rebalance the whole split
    (fee = amount − seller; partner capped at fee) — payouts can never exceed
    the amount collected."""
    from app.controlplane.services.marketplace import split_economics

    amount = 10000
    fee, seller, partner = split_economics(amount, Decimal("20"), Decimal("15"))
    assert fee == 2000 and seller == 8000 and partner == 1500
    # Simulate the create_purchase override math with a 90% seller rule:
    seller = min(int(Decimal(amount) * Decimal("90") / 100), amount)
    fee = amount - seller
    partner = min(partner, fee)
    assert seller == 9000 and fee == 1000 and partner == 1000
    assert fee + seller <= amount and seller + partner <= amount


@pytest.mark.asyncio
async def test_second_manual_adjustment_no_unique_violation(db):
    """R50[41]/R73: a SECOND manual adjustment on the same statement previously
    violated uq_cp_revshare_natural (identical natural key) → 500. Each manual
    adjustment now carries a distinct self-referencing adjustment_of_id."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    invoice = await _mk_invoice(db, tenant, subtotal=10000)
    await revshare_svc.accrue_for_invoice(db, invoice.id)
    stmt = await revshare_svc.generate_statement(
        db,
        beneficiary_type="partner",
        partner_id=partner.id,
        beneficiary_org_id=None,
        period=invoice.finalized_at.strftime("%Y-%m"),
        actor=_actor(user),
    )
    s1 = await revshare_svc.adjust_statement(
        db, stmt, amount_minor=-100, reason="dispute 1", actor=_actor(user)
    )
    s2 = await revshare_svc.adjust_statement(
        db, s1, amount_minor=-50, reason="dispute 2", actor=_actor(user)
    )
    assert s2.manual_adjustments_minor == -150


@pytest.mark.asyncio
async def test_void_rated_guarded_against_terminal_states(db):
    """R73[6]: void_rated must be a guarded transition — an invoiced or settled
    row can never be flipped to voided by a stale read."""
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services import rating

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    ev = UsageEvent(
        id=str(ULID()),
        tenant_id=tenant.id,
        org_id=str(ULID()),
        usage_type="image_generation",
        quantity=1,
        unit="images",
        occurred_at=datetime.now(UTC),
        source="manual",
    )
    db.add(ev)
    await db.flush()
    row = RatedUsage(
        usage_event_id=ev.id,
        tenant_id=tenant.id,
        org_id=ev.org_id,
        usage_type="image_generation",
        quantity=1,
        cost_rate_snapshot={},
        internal_cost_minor=0,
        internal_cost_currency="USD",
        sell_rate_snapshot={},
        billable_amount_minor=100,
        billable_amount_exact=Decimal(100),
        billable_currency="USD",
        status="settled",  # terminal: paid via credit reservation
        rated_at=datetime.now(UTC),
    )
    db.add(row)
    await db.flush()
    with pytest.raises(AppError) as exc:
        await rating.void_rated(db, row.id, reason="oops", actor=_actor(user))
    assert exc.value.code == "RATED_USAGE_INVOICED"
    await db.refresh(row)
    assert row.status == "settled"  # untouched


# ── R60: margin leak + audit completeness ─────────────────────


@pytest.mark.asyncio
async def test_partner_entry_response_hides_margin_base(db):
    """R60[39]: for percentage_of_margin rules, revenue_base_minor IS the
    platform's internal margin — partner-facing responses and the CSV export
    must not expose it. Percentage-of-gross entries keep their base."""
    from app.controlplane.api.partners import _entry_response, _margin_based

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    margin_entry = RevenueShareEntry(
        beneficiary_type="partner",
        partner_id=partner.id,
        source_type="invoice",
        source_id=str(ULID()),
        rule_snapshot={"rule_type": "percentage_of_margin", "rate": "30"},
        revenue_base_minor=15000,  # internal margin — must not leak
        share_amount_minor=4500,
        currency="USD",
        period="2026-09",
    )
    gross_entry = RevenueShareEntry(
        beneficiary_type="partner",
        partner_id=partner.id,
        source_type="invoice",
        source_id=str(ULID()),
        rule_snapshot={"rule_type": "percentage_of_gross_revenue", "rate": "10"},
        revenue_base_minor=100000,
        share_amount_minor=10000,
        currency="USD",
        period="2026-09",
    )
    db.add_all([margin_entry, gross_entry])
    await db.flush()
    await db.refresh(margin_entry)
    await db.refresh(gross_entry)
    assert _margin_based(margin_entry) is True
    assert _entry_response(margin_entry)["revenue_base_minor"] is None
    assert _entry_response(gross_entry)["revenue_base_minor"] == 100000


@pytest.mark.asyncio
async def test_rule_retirement_is_audited(db):
    """R60[41]: activating v2 retires v1 — the retirement must be audited with
    the RETIRED rule as target (registry action revshare.rule_retired had zero
    emit sites)."""
    from app.controlplane.models.audit import CommercialAuditEvent

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    r1 = await _mk_rule(db, user, partner, rate="10", version=1)
    await _mk_rule(db, user, partner, rate="12", version=2)
    events = (
        (
            await db.execute(
                select(CommercialAuditEvent).where(
                    CommercialAuditEvent.action == "revshare.rule_retired",
                    CommercialAuditEvent.target_id == r1.id,
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(events) == 1
    assert events[0].after["superseded_by"] is not None


@pytest.mark.asyncio
async def test_credit_note_retry_covers_dead_lettered_finalize(db):
    """R129[M7]: the credit_note.applied outrun retry (R123[H7]) counted only
    pending/processing invoice.finalized rows — a DEAD-LETTERED finalize let
    the reversal complete as done, and after ops requeued the finalize the
    negative adjustment was permanently undriveable. The gate must also retry
    over a 'failed' finalize so the pair stays requeueable together."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.controlplane.services.revenue_share import _handle_credit_note

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    invoice = Invoice(
        tenant_id=tenant.id,
        status="open",
        currency="USD",
        subtotal_minor=10000,
        total_minor=10000,
        amount_due_minor=10000,
    )
    db.add(invoice)
    await db.flush()
    # The finalize accrual dead-lettered before running (no entries exist).
    db.add(
        OutboxMessage(
            topic="invoice.finalized",
            payload={"invoice_id": invoice.id},
            status="failed",
            attempts=8,
        )
    )
    await db.flush()
    with pytest.raises(RuntimeError, match="not yet processed"):
        await _handle_credit_note(
            db, {"credit_note_id": "01JBLNOTE0000000000000000X", "invoice_id": invoice.id}
        )


@pytest.mark.asyncio
async def test_void_after_credit_note_nets_history_to_zero(db):
    """R139: reverse_invoice_accruals claimed to net an invoice's rev-share
    history to zero (R97[m13]), but its query filtered source_type=='invoice'
    while credit-note adjustments carry source_type=='invoice_line'
    (source_id=note.id). A credit note on an OPEN invoice followed by a void
    left the note's negative adjustment standing — after the re-close the
    partner was UNDER-paid by the note's reversal amount."""
    from app.controlplane.models.billing import CreditNote

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="30")
    invoice = await _mk_invoice(db, tenant, subtotal=1000)
    orig = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert orig.share_amount_minor == 300
    # Credit note on the still-open invoice: 400/1000 → -120 adjustment.
    note = CreditNote(
        invoice_id=invoice.id,
        tenant_id=tenant.id,
        amount_minor=400,
        currency="USD",
        reason="partial",
        status="applied",
    )
    db.add(note)
    await db.flush()
    n_adj = await revshare_svc.accrue_credit_note(db, note.id, invoice.id)
    assert n_adj == 1
    # Void the invoice → the WHOLE history for this invoice must net to zero
    # (original + note adjustment + their reversals), so the re-close's fresh
    # accrual is the partner's only standing entry for the revenue.
    await revshare_svc.reverse_invoice_accruals(db, invoice.id)
    live = (
        (
            await db.execute(
                select(RevenueShareEntry).where(
                    (RevenueShareEntry.source_id == invoice.id)
                    | (RevenueShareEntry.source_id == note.id)
                )
            )
        )
        .scalars()
        .all()
    )
    assert sum(e.share_amount_minor for e in live) == 0, (
        f"void left {sum(e.share_amount_minor for e in live)} standing — "
        "partner under-paid by the note reversal"
    )
    # Idempotent second pass.
    assert await revshare_svc.reverse_invoice_accruals(db, invoice.id) == 0


@pytest.mark.asyncio
async def test_accrual_base_per_rule_type(db):
    """R261: three of five rule types' accrual BASES were untested end-to-end
    — net = total − tax; margin = platform-currency margin_minor sum over the
    invoice's rated rows; per-seat units derive from amount/unit_amount so a
    TRUNCATED period's prorated seats line pays prorated rev-share (R129[H5],
    which had no regression sentinel)."""
    from app.controlplane.models.billing import InvoiceLine
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)

    # net revenue: 15% of (total 2000_00 − tax 200_00) = 270_00
    await _mk_rule(db, user, partner, rate="15", rule_type="percentage_of_net_revenue")
    inv = await _mk_invoice(db, tenant, subtotal=180000)
    inv.tax_minor = 20000
    inv.total_minor = 200000
    await db.flush()
    entry = await revshare_svc.accrue_for_invoice(db, inv.id)
    assert entry.share_amount_minor == 27000

    # margin: 25% of the summed margin_minor (platform currency)
    user2 = await _mk_user(db)
    partner2 = await _mk_partner(db, user2)
    tenant2 = await _mk_tenant(db, user2, partner2)
    await _mk_rule(db, user2, partner2, rate="25", rule_type="percentage_of_margin")
    inv2 = await _mk_invoice(db, tenant2, subtotal=500000)
    line = InvoiceLine(
        invoice_id=inv2.id, line_type="usage", description="u",
        quantity=1, unit_amount_minor=500000, amount_minor=500000)
    db.add(line)
    await db.flush()
    from app.models.organization import Organization

    org2 = Organization(
        name=f"RS {ULID()}", slug=f"rs-{str(ULID()).lower()}",
        tenant_id=tenant2.id, created_by=user2.id)
    db.add(org2)
    await db.flush()
    eid = str(ULID())
    db.add(UsageEvent(
        id=eid, tenant_id=tenant2.id, org_id=org2.id, usage_type="image_generation",
        quantity=1, unit="images", occurred_at=datetime.now(UTC), source="manual"))
    await db.flush()
    db.add(RatedUsage(
        usage_event_id=eid, tenant_id=tenant2.id, org_id=org2.id,
        usage_type="image_generation", quantity=1, cost_rate_snapshot={},
        internal_cost_minor=300000, internal_cost_currency="USD",
        sell_rate_snapshot={}, billable_amount_minor=500000,
        billable_amount_exact=Decimal(500000), billable_currency="USD",
        margin_minor=200000, status="invoiced", rated_at=datetime.now(UTC),
        invoice_line_id=line.id))
    await db.flush()
    entry2 = await revshare_svc.accrue_for_invoice(db, inv2.id)
    assert entry2.share_amount_minor == 50000        # 25% of 2000_00 margin

    # per-seat on a truncated period: seats line amount prorated to 50% —
    # units must be amount/unit_amount (5), not the full quantity (10)
    user3 = await _mk_user(db)
    partner3 = await _mk_partner(db, user3)
    tenant3 = await _mk_tenant(db, user3, partner3)
    seat_rule = RevenueShareRule(
        beneficiary_type="partner", partner_id=partner3.id, revenue_type="all",
        rule_type="fixed_amount_per_seat", rate=None, amount_minor=200,
        amount_currency="USD", version=1,
        effective_from=datetime.now(UTC) - timedelta(days=30), created_by=user3.id)
    db.add(seat_rule)
    await db.flush()
    await revshare_svc.activate_rule(
        db, seat_rule, actor=Actor(user_id=user3.id, type="platform"))
    inv3 = await _mk_invoice(db, tenant3, subtotal=50000)
    db.add(InvoiceLine(
        invoice_id=inv3.id, line_type="seats", description="seats",
        quantity=10, unit_amount_minor=10000, amount_minor=50000))  # half period
    await db.flush()
    entry3 = await revshare_svc.accrue_for_invoice(db, inv3.id)
    assert entry3.share_amount_minor == 200 * 5      # prorated units, not 10


@pytest.mark.asyncio
async def test_accrue_refund_mirrors_and_replay_noop(db):
    """R262: a marketplace refund writes negative adjusted mirrors of the
    purchase's accruals; an outbox redelivery must NOT double-reverse (the
    natural key includes adjustment_of_id)."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    pid = str(ULID())
    original = await revshare_svc._insert_entry(
        db,
        beneficiary_type="partner", partner_id=partner.id, beneficiary_org_id=None,
        source_type="marketplace_purchase", source_id=pid,
        rule_id=None, rule_snapshot={"rate": "30"},
        revenue_base_minor=10000, share_amount_minor=3000,
        currency="USD", period="2026-09", status="accrued")
    assert original is not None

    n = await revshare_svc.accrue_refund(db, pid)
    assert n == 1
    mirror = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.adjustment_of_id == original.id))
    ).scalar_one()
    assert mirror.share_amount_minor == -3000
    assert mirror.revenue_base_minor == -10000
    assert mirror.status == "adjusted"
    assert mirror.rule_snapshot.get("void_reversal") is True

    assert await revshare_svc.accrue_refund(db, pid) == 0   # replay no-op


@pytest.mark.asyncio
async def test_fixed_amount_rule_fx_conversion_and_missing_rate(db):
    """R262: a fixed-amount rule denominated in another currency converts at
    accrual time; a missing FX rate is a 409 (retryable), never a silent
    unconverted amount."""
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    rule = RevenueShareRule(
        beneficiary_type="partner", partner_id=partner.id, revenue_type="all",
        rule_type="fixed_amount_per_unit", rate=None, amount_minor=1000,
        amount_currency="EUR", version=1,
        effective_from=datetime.now(UTC) - timedelta(days=30), created_by=user.id)
    db.add(rule)
    await db.flush()
    await revshare_svc.activate_rule(db, rule, actor=Actor(user_id=user.id, type="platform"))

    inv = await _mk_invoice(db, tenant, subtotal=100000)    # USD invoice
    with pytest.raises(AppError) as e:                      # no EUR->USD rate
        await revshare_svc.accrue_for_invoice(db, inv.id)
    assert e.value.code == "REVSHARE_FX_MISSING" and e.value.status_code == 409

    await pricing_svc.create_fx_rate(
        db, actor=Actor(user_id=user.id, type="platform"),
        base_currency="EUR", quote_currency="USD", rate=Decimal("2"),
        effective_from=datetime.now(UTC) - timedelta(days=1))
    entry = await revshare_svc.accrue_for_invoice(db, inv.id)
    assert entry.share_amount_minor == 2000                 # 1000 EUR-minor × 2


@pytest.mark.asyncio
async def test_invoice_accrual_converts_to_partner_currency(db):
    """R263: the SUCCESS arm of the invoice-path partner-currency conversion
    (only the missing-rate 409 was tested) — share AND base convert at the
    resolved rate."""
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    partner.currency = "EUR"
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    await db.flush()
    await pricing_svc.create_fx_rate(
        db, actor=_actor(user), base_currency="USD", quote_currency="EUR",
        rate=Decimal("0.5"), effective_from=datetime.now(UTC) - timedelta(days=1))
    invoice = await _mk_invoice(db, tenant, subtotal=100000)  # $1000 USD
    entry = await revshare_svc.accrue_for_invoice(db, invoice.id)
    assert entry.currency == "EUR"
    assert entry.share_amount_minor == 5000            # 10% of $1000 → €50.00
    assert entry.revenue_base_minor == 50000           # base converted too


@pytest.mark.asyncio
async def test_purchase_accrual_guards(db):
    """R263: accrue_for_purchase's guard arcs — unknown purchase and unpaid
    purchase are clean no-ops; a TERMINATED partner stops NEW purchase
    accruals (R113[H4]'s purchase-path sibling — only the invoice path had a
    sentinel)."""
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)

    assert await revshare_svc.accrue_for_purchase(db, str(ULID())) == 0  # unknown

    listing = MarketplaceListing(
        product_type="workflow_pack", product_id=str(ULID()),
        seller_org_id=str(ULID()), seller_tenant_id=str(ULID()),
        offer_type="paid", price_minor=10000, currency="USD",
        platform_commission_pct=Decimal("20"), status="active", created_by=user.id)
    db.add(listing)
    await db.flush()

    def mk_purchase(status="paid"):
        return MarketplacePurchase(
            listing_id=listing.id, buyer_tenant_id=tenant.id,
            buyer_org_id=str(ULID()), purchaser_user_id=user.id, status=status,
            amount_minor=10000, currency="USD", platform_fee_minor=2000,
            seller_share_minor=7000, partner_share_minor=1000,
            economics_snapshot={"partner_id": partner.id, "seller_org_id": None})

    pending = mk_purchase(status="pending")
    db.add(pending)
    await db.flush()
    assert await revshare_svc.accrue_for_purchase(db, pending.id) == 0   # unpaid

    partner.status = "terminated"
    await db.flush()
    paid = mk_purchase()
    db.add(paid)
    await db.flush()
    assert await revshare_svc.accrue_for_purchase(db, paid.id) == 0      # terminated
    entries = (
        (await db.execute(
            select(RevenueShareEntry).where(RevenueShareEntry.source_id == paid.id)))
        .scalars().all()
    )
    assert entries == []


@pytest.mark.asyncio
async def test_refund_before_accrual_retries_until_paid_lands(db):
    """R263: purchase.refunded arriving BEFORE purchase.paid was processed —
    the handler must RAISE (outbox retries) while a live/failed paid message
    exists, and no-op silently only when the purchase legitimately has no
    accruals (R129[M7]: including dead-lettered originals keeps both
    requeueable together)."""
    from app.controlplane.models.outbox import OutboxMessage, enqueue
    from app.controlplane.services.revenue_share import _handle_purchase_refunded

    pid = str(ULID())
    # free/partner-less purchase: no accruals, no pending paid → clean no-op
    await _handle_purchase_refunded(db, {"purchase_id": pid})

    enqueue(db, "purchase.paid", {"purchase_id": pid})       # paid still queued
    await db.flush()
    with pytest.raises(RuntimeError, match="not yet processed"):
        await _handle_purchase_refunded(db, {"purchase_id": pid})

    msg = (
        await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "purchase.paid",
                OutboxMessage.payload["purchase_id"].astext == pid))
    ).scalar_one()
    msg.status = "failed"                                    # dead-lettered original
    await db.flush()
    with pytest.raises(RuntimeError, match="not yet processed"):
        await _handle_purchase_refunded(db, {"purchase_id": pid})  # R129[M7]

    msg.status = "done"                                      # processed (no accruals)
    await db.flush()
    await _handle_purchase_refunded(db, {"purchase_id": pid})  # now a clean no-op


@pytest.mark.asyncio
async def test_settlement_transition_guards_and_entry_flips(db):
    """R306: settlement state machine — an ordered pipeline moving partner
    money. Pins: mark-paid REQUIRES an external_payment_ref (a payout marked
    paid with no wire reference is untraceable money movement); approve flips
    the statement's entries to 'approved' and mark-paid to 'settled' (the
    entry money-state follows the statement); every out-of-order transition
    is a 409; an unknown action is 422; and an approved/paid statement can no
    longer be adjusted."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    period = datetime.now(UTC).strftime("%Y-%m")
    await revshare_svc.accrue_for_invoice(db, (await _mk_invoice(db, tenant, subtotal=100000)).id)

    async def fresh_statement():
        return await revshare_svc.generate_statement(
            db, beneficiary_type="partner", partner_id=partner.id,
            beneficiary_org_id=None, period=period, actor=_actor(user))

    st = await fresh_statement()

    # unknown action → 422
    with pytest.raises(AppError) as e:
        await revshare_svc.transition_statement(db, st, "teleport", actor=_actor(user))
    assert e.value.code == "VALIDATION_ERROR" and e.value.status_code == 422

    # out-of-order from draft: approve and mark-paid both 409
    for bad in ("approve", "mark-paid"):
        with pytest.raises(AppError) as e:
            await revshare_svc.transition_statement(
                db, st, bad, actor=_actor(user), external_payment_ref="W")
        assert e.value.code == "STATEMENT_STATUS_CONFLICT" and e.value.status_code == 409

    st = await revshare_svc.transition_statement(db, st, "finalize", actor=_actor(user))
    assert st.status == "finalized"

    # mark-paid without a payment ref → 422 (untraceable payout guard)
    st = await revshare_svc.transition_statement(db, st, "approve", actor=_actor(user))
    with pytest.raises(AppError) as e:
        await revshare_svc.transition_statement(db, st, "mark-paid", actor=_actor(user))
    assert e.value.code == "VALIDATION_ERROR" and "external_payment_ref" in e.value.message
    assert e.value.status_code == 422  # R344

    # after approve, entries are 'approved' (not yet settled)
    def entry_statuses():
        return db.execute(
            select(RevenueShareEntry.status).where(
                RevenueShareEntry.statement_id == st.id))
    approved = {r for (r,) in (await entry_statuses()).all()}
    assert approved == {"approved"}

    # cannot adjust an approved statement
    with pytest.raises(AppError) as e:
        await revshare_svc.adjust_statement(
            db, st, amount_minor=-100, reason="late", actor=_actor(user))
    assert e.value.code == "STATEMENT_STATUS_CONFLICT" and e.value.status_code == 409

    st = await revshare_svc.transition_statement(
        db, st, "mark-paid", actor=_actor(user), external_payment_ref="WIRE-99")
    assert st.status == "paid_externally"
    settled = {r for (r,) in (await entry_statuses()).all()}
    assert settled == {"settled"}


@pytest.mark.asyncio
async def test_accrual_gates_and_per_seat_free_line(db):
    """R344 (mutation survivors): (1) a DRAFT invoice never accrues; (2) an
    OPEN invoice whose finalized_at is NULL still accrues (`at` falls back to
    now — the Or→And mutant silently skips it); (3) per-seat units on a FREE
    seats line (unit_amount 0) fall back to the line quantity, not zero. The
    percentage-branch `units = 1` mutants are equivalent (amount_minor is
    None for percentage rules, so units multiplies nothing) — documented."""
    from app.controlplane.models.billing import InvoiceLine

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")

    draft = await _mk_invoice(db, tenant)
    draft.status = "draft"
    await db.flush()
    assert await revshare_svc.accrue_for_invoice(db, draft.id) is None

    unfinalized = await _mk_invoice(db, tenant, subtotal=50000)
    unfinalized.finalized_at = None
    await db.flush()
    entry = await revshare_svc.accrue_for_invoice(db, unfinalized.id)
    assert entry is not None and entry.share_amount_minor == 5000

    # per-seat rule: free seats line (unit_amount 0, qty 3) → units == 3
    partner2 = await _mk_partner(db, user)
    tenant2 = await _mk_tenant(db, user, partner2)
    await _mk_rule(db, user, partner2, rule_type="fixed_amount_per_seat",
                   rate="0", amount_minor=200, amount_currency="USD",
                   revenue_type="subscription")
    inv = await _mk_invoice(db, tenant2, subtotal=0)
    db.add(InvoiceLine(
        invoice_id=inv.id, line_type="seats", description="free seats",
        quantity=3, unit_amount_minor=0, amount_minor=0))
    await db.flush()
    e2 = await revshare_svc.accrue_for_invoice(db, inv.id)
    assert e2 is not None and e2.share_amount_minor == 600     # 3 × $2.00


@pytest.mark.asyncio
async def test_purchase_accrual_seller_fx_counts_and_snapshots(db):
    """R344: the SELLER path (R56[22] only pinned the partner path) —
    (1) a non-platform-currency purchase's seller entry converts to the
    platform currency; (2) a purchase with no seller_rule_snapshot writes the
    from_economics_snapshot marker, never null; (3) the return value counts
    BOTH entries once each; (4) a same-currency partner entry carries NO fx
    snapshot; (5) a missing seller-FX rate is a 409, not a silent buyer-
    currency entry; (6) no partner in the snapshot → seller entry only.
    Documented-equivalent mutants: percentage-branch units=1 (amount_minor is
    None so units multiplies nothing); the tenant/partner_id Or (redundant
    with the partner-None return, tenant FK-guaranteed); the refund share>0
    guard (0-share originals are never created — the partner_share gate skips
    them); the refund snapshot  (originals always carry a snapshot via
    the from_economics_snapshot fallback)."""
    from app.controlplane.models.marketplace import MarketplaceListing, MarketplacePurchase
    from app.controlplane.services import pricing as pricing_svc

    user = await _mk_user(db)
    partner = await _mk_partner(db, user)  # USD partner
    tenant = await _mk_tenant(db, user, partner)
    await pricing_svc.create_fx_rate(
        db, actor=_actor(user), base_currency="JPY", quote_currency="USD",
        rate=Decimal("0.0066667"),
        effective_from=datetime.now(UTC) - timedelta(days=1))

    def _listing(cur):
        return MarketplaceListing(
            product_type="workflow_pack", product_id=str(ULID()),
            seller_org_id=str(ULID()), seller_tenant_id=str(ULID()),
            offer_type="paid", price_minor=150000, currency=cur,
            platform_commission_pct=Decimal("20"), status="active",
            created_by=user.id)

    def _purchase(listing, cur, *, partner_id, seller_org):
        return MarketplacePurchase(
            listing_id=listing.id, buyer_tenant_id=tenant.id,
            buyer_org_id=str(ULID()), purchaser_user_id=user.id, status="paid",
            amount_minor=150000, currency=cur, platform_fee_minor=30000,
            seller_share_minor=120000, partner_share_minor=15000,
            economics_snapshot={"partner_id": partner_id,
                                "seller_org_id": seller_org})

    # (1)(2)(3): JPY purchase with seller + partner
    l1 = _listing("JPY")
    db.add(l1)
    await db.flush()
    seller_org = str(ULID())
    p1 = _purchase(l1, "JPY", partner_id=partner.id, seller_org=seller_org)
    db.add(p1)
    await db.flush()
    created = await revshare_svc.accrue_for_purchase(db, p1.id)
    assert created == 2                                   # seller + partner, once each
    seller_entry = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.source_id == p1.id,
                RevenueShareEntry.beneficiary_type == "seller_org"))
    ).scalar_one()
    assert seller_entry.currency == "USD"                 # platform currency
    assert abs(seller_entry.share_amount_minor - 80000) <= 4  # ¥120,000 → ~$800
    assert seller_entry.rule_snapshot == {"from_economics_snapshot": True}

    # (4): USD purchase, USD partner → no FX snapshot on the partner entry
    l2 = _listing("USD")
    db.add(l2)
    await db.flush()
    p2 = _purchase(l2, "USD", partner_id=partner.id, seller_org=None)
    db.add(p2)
    await db.flush()
    assert await revshare_svc.accrue_for_purchase(db, p2.id) == 1
    partner_entry = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.source_id == p2.id,
                RevenueShareEntry.beneficiary_type == "partner"))
    ).scalar_one()
    assert partner_entry.fx_rate_snapshot is None
    assert partner_entry.currency == "USD"

    # (6): no partner in the snapshot → only the seller entry
    l3 = _listing("USD")
    db.add(l3)
    await db.flush()
    p3 = _purchase(l3, "USD", partner_id=None, seller_org=str(ULID()))
    db.add(p3)
    await db.flush()
    assert await revshare_svc.accrue_for_purchase(db, p3.id) == 1
    kinds = (
        await db.execute(
            select(RevenueShareEntry.beneficiary_type).where(
                RevenueShareEntry.source_id == p3.id))
    ).scalars().all()
    assert kinds == ["seller_org"]

    # (5): GBP purchase with NO GBP→USD rate → 409, never a buyer-currency entry
    l4 = _listing("GBP")
    db.add(l4)
    await db.flush()
    p4 = _purchase(l4, "GBP", partner_id=None, seller_org=str(ULID()))
    db.add(p4)
    await db.flush()
    with pytest.raises(AppError) as e409:
        await revshare_svc.accrue_for_purchase(db, p4.id)
    assert e409.value.code == "REVSHARE_FX_MISSING" and e409.value.status_code == 409

    # (7): the partner entry ALSO writes the marker snapshot when the
    # economics snapshot has no partner_rule_snapshot
    assert partner_entry.rule_snapshot == {"from_economics_snapshot": True}

    # (8): partner in a THIRD currency with no rate → 409 with status
    from app.controlplane.models.partner import Partner as _Partner

    eur_partner = _Partner(name=f"EURP {ULID()}", slug=f"eurp-{str(ULID()).lower()[:10]}",
                           currency="EUR", status="active", partner_type="reseller", created_by=user.id)
    db.add(eur_partner)
    await db.flush()
    l5 = _listing("USD")
    db.add(l5)
    await db.flush()
    p5 = _purchase(l5, "USD", partner_id=eur_partner.id, seller_org=None)
    db.add(p5)
    await db.flush()
    with pytest.raises(AppError) as e409b:
        await revshare_svc.accrue_for_purchase(db, p5.id)
    assert e409b.value.code == "REVSHARE_FX_MISSING" and e409b.value.status_code == 409

    # (9): refunds mirror only POSITIVE originals, copying the snapshot with
    # the void_reversal marker (a null original snapshot still yields a dict)
    n_ref = await revshare_svc.accrue_refund(db, p2.id)
    assert n_ref == 1
    mirror = (
        await db.execute(
            select(RevenueShareEntry).where(
                RevenueShareEntry.source_id == p2.id,
                RevenueShareEntry.adjustment_of_id.is_not(None)))
    ).scalar_one()
    assert mirror.share_amount_minor == -partner_entry.share_amount_minor
    assert mirror.rule_snapshot.get("void_reversal") is True
    # replaying the refund does not re-mirror (natural-key idempotent), and
    # the negative mirrors themselves are never mirrored (> 0 guard)
    assert await revshare_svc.accrue_refund(db, p2.id) == 0


@pytest.mark.asyncio
async def test_generate_statement_boundaries(db):
    """R375 (generate_statement survivors): (1) an unknown partner is a 404
    and an org-type statement without an org id is a 422; (2) regenerating a
    period statement while it is DRAFT recomputes in place, while a FINALIZED
    one is a 409; (3) gross counts POSITIVE bases only and refunds NEGATIVE
    only — a mixed period (accrual + refund mirror) splits exactly; (4) the
    org-scoped entry filter never sweeps a partner's entries."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)
    await _mk_rule(db, user, partner, rate="10")
    a = _actor(user)

    # (1) statuses
    with pytest.raises(AppError) as e404:
        await revshare_svc.generate_statement(
            db, beneficiary_type="partner", partner_id=str(ULID()),
            beneficiary_org_id=None, period="2026-09", actor=a)
    assert e404.value.status_code == 404
    with pytest.raises(AppError) as e422:
        await revshare_svc.generate_statement(
            db, beneficiary_type="seller_org", partner_id=None,
            beneficiary_org_id=None, period="2026-09", actor=a)
    assert e422.value.status_code == 422

    # (3) mixed period: +1000 accrual and its -1000 refund mirror
    inv = await _mk_invoice(db, tenant, subtotal=10000)
    entry = await revshare_svc.accrue_for_invoice(db, inv.id)
    assert entry is not None and entry.share_amount_minor == 1000
    period = entry.period
    from app.controlplane.models.partner import RevenueShareEntry as REntry

    db.add(REntry(beneficiary_type="partner", partner_id=partner.id,
              source_type="invoice", source_id=inv.id, rule_snapshot={},
              revenue_base_minor=-4000, share_amount_minor=-400,
              currency=partner.currency, period=period, status="adjusted",
              adjustment_of_id=entry.id))
    await db.flush()

    st = await revshare_svc.generate_statement(
        db, beneficiary_type="partner", partner_id=partner.id,
        beneficiary_org_id=None, period=period, actor=a)
    assert st.gross_revenue_minor == 10000          # positive bases only
    assert st.refunds_minor == -4000                # negative bases only
    assert st.share_total_minor == 600              # 1000 − 400
    assert st.status == "draft"

    # (2) draft regenerate recomputes IN PLACE (same row)
    st2 = await revshare_svc.generate_statement(
        db, beneficiary_type="partner", partner_id=partner.id,
        beneficiary_org_id=None, period=period, actor=a)
    assert st2.id == st.id
    # finalized → 409
    await revshare_svc.transition_statement(db, st, "finalize", actor=a)
    with pytest.raises(AppError) as e409:
        await revshare_svc.generate_statement(
            db, beneficiary_type="partner", partner_id=partner.id,
            beneficiary_org_id=None, period=period, actor=a)
    assert e409.value.code == "STATEMENT_STATUS_CONFLICT" and e409.value.status_code == 409

    # (4) an ORG-scoped statement for some org never sweeps the partner's
    # entries (the flipped org filter would)
    org_id = str(ULID())
    st_org = await revshare_svc.generate_statement(
        db, beneficiary_type="seller_org", partner_id=None,
        beneficiary_org_id=org_id, period=period, actor=a)
    assert st_org.share_total_minor == 0            # nothing for that org
    # org-type regenerate finds ITS OWN draft (the flipped org filter builds
    # a duplicate row instead)
    st_org2 = await revshare_svc.generate_statement(
        db, beneficiary_type="seller_org", partner_id=None,
        beneficiary_org_id=org_id, period=period, actor=a)
    assert st_org2.id == st_org.id
    # (zero-base entries are numeric no-ops on both gross and refunds — the
    # strict comparisons' boundary mutants are sum-with-zero equivalents; the
    # reversal-snapshot 'or {}' is unreachable-None — documented.)


@pytest.mark.asyncio
async def test_rule_tiebreak_typed_beats_all_then_version(db):
    """R376 (_resolve_rule survivors): at EQUAL specificity a rule typed to
    the revenue stream beats an 'all' rule regardless of version, and among
    equal (spec, type) the HIGHER version wins."""
    user = await _mk_user(db)
    partner = await _mk_partner(db, user)
    tenant = await _mk_tenant(db, user, partner)

    def _active_rule(rate, version, rtype):
        return RevenueShareRule(
            beneficiary_type="partner", partner_id=partner.id,
            revenue_type=rtype, rule_type="percentage_of_gross_revenue",
            rate=Decimal(rate), version=version, status="active",
            effective_from=datetime.now(UTC) - timedelta(days=30),
            created_by=user.id)

    # 'all' at a high version vs TYPED at low version → typed wins
    # (direct active rows: this pins _resolve_rule's ORDERING, not the
    # activation flow's same-dims retirement)
    db.add_all([_active_rule("50", 9, "all"),
                _active_rule("10", 1, "subscription")])
    await db.flush()
    inv = await _mk_invoice(db, tenant, subtotal=100000)
    entry = await revshare_svc.accrue_for_invoice(db, inv.id)
    # the TYPED rule won the tie (its R56[23] typed base is 0 on a line-less
    # invoice — the 'all' rule would have accrued 50% of the full 100000)
    snap = entry.rule_snapshot or {}
    assert str(snap.get("rate", "")).startswith("10"), snap
    assert entry.share_amount_minor == 0            # typed slice, no sub lines
    # two TYPED rules: higher version wins the (spec, type) tie
    db.add(_active_rule("20", 2, "subscription"))
    await db.flush()
    inv2 = await _mk_invoice(db, tenant, subtotal=100000)
    entry2 = await revshare_svc.accrue_for_invoice(db, inv2.id)
    snap2 = entry2.rule_snapshot or {}
    assert str(snap2.get("rate", "")).startswith("20"), snap2   # v2 beats v1
    # (an IDENTICAL (spec, type, version) key pair is constraint-impossible —
    # uq_cp_revshare_rule_version — so the best-key >= mutant is a
    # constraint-equivalent, verified empirically: the second row 23505s.)
