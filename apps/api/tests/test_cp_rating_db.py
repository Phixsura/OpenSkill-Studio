"""P4 DB tests: cost ladder, policy specificity, FX blocking, snapshots,
concurrency, reconciliation."""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import metering, rating
from app.controlplane.services import pricing as pricing_svc
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
        email=f"cp4-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP4",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user, currency="USD") -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"R {ULID()}",
        slug=f"r-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
        currency=currency,
    )


async def _mk_event(db, tenant, **kw):
    defaults = dict(
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=10,
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=f"re-{ULID()}",
    )
    defaults.update(kw)
    return await metering.emit_usage(db, **defaults)


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── Pure computation ─────────────────────────────────────────


def test_apply_tiers():
    tiers = [
        {"min_qty": "0", "unit_cost": "0.018"},
        {"min_qty": "1000", "unit_cost": "0.015"},
    ]
    assert rating.apply_tiers(Decimal("0.02"), tiers, Decimal("500")) == Decimal("0.018")
    assert rating.apply_tiers(Decimal("0.02"), tiers, Decimal("1000")) == Decimal("0.015")
    assert rating.apply_tiers(Decimal("0.02"), None, Decimal("5")) == Decimal("0.02")


def test_compute_internal_cost():
    # $0.018/image × 10 images = $0.18 = 18 minor
    assert rating.compute_internal_cost_minor(Decimal("0.018"), Decimal(10), "USD", None) == 18
    # minimum fee floors it
    assert rating.compute_internal_cost_minor(Decimal("0.018"), Decimal(10), "USD", 50) == 50
    # JPY: 0-decimal currency
    assert rating.compute_internal_cost_minor(Decimal("2.6"), Decimal(10), "JPY", None) == 26


def test_compute_billable_matrix():
    f = rating.compute_billable_minor
    # cost+50%: 100 minor cost → 150
    assert (
        f(
            "cost_plus_percentage",
            {"percentage": "50"},
            internal_cost_minor=100,
            quantity=Decimal(1),
        )
        == 150
    )
    # cost + fixed 500 per unit
    assert (
        f(
            "cost_plus_fixed",
            {"fixed_markup_minor": 500},
            internal_cost_minor=100,
            quantity=Decimal(2),
        )
        == 100 + 1000
    )
    # R7: markup is per STARTED block → ⌈qty/per⌉, never round-half-up.
    # A partial block (1400/1000) bills 2 blocks, not 1 (was an under-bill).
    for qty, blocks in ((1000, 1), (1001, 2), (1400, 2), (2000, 2), (2001, 3)):
        assert (
            f(
                "cost_plus_fixed",
                {"fixed_markup_minor": 500, "per_quantity": "1000"},
                internal_cost_minor=0,
                quantity=Decimal(qty),
            )
            == 500 * blocks
        ), qty
    # fixed unit price: 3 minor per 1000 tokens × 2000 tokens = 6
    assert (
        f(
            "fixed_unit_price",
            {"unit_price_minor": 3, "per_quantity": "1000"},
            internal_cost_minor=0,
            quantity=Decimal(2000),
        )
        == 6
    )
    # included quota then overage: 100k included, 2/1k over; prior 99k + 3k now → 2k over
    assert (
        f(
            "included_quota_then_overage",
            {"included_quota": "100000", "overage_unit_price_minor": 2, "per_quantity": "1000"},
            internal_cost_minor=0,
            quantity=Decimal(3000),
            prior_period_quantity=Decimal(99000),
        )
        == 4
    )
    # exclude_failed
    assert (
        f(
            "cost_plus_percentage",
            {"percentage": "50", "exclude_failed": True},
            internal_cost_minor=100,
            quantity=Decimal(1),
            usage_metadata={"status": "failed"},
        )
        == 0
    )


def test_policy_params_validation():
    v = pricing_svc.validate_policy_params
    v("cost_plus_percentage", {"percentage": "66.7"})
    v("fixed_unit_price", {"unit_price_minor": 3, "per_quantity": "1000"})
    for policy_type, params in [
        ("cost_plus_percentage", {}),
        ("cost_plus_percentage", {"percentage": "NaN"}),
        ("cost_plus_percentage", {"percentage": "50", "bogus": 1}),
        ("fixed_unit_price", {"unit_price_minor": -1}),
        ("included_quota_then_overage", {"included_quota": "1"}),
        ("nope", {}),
        # R52[12]: per_quantity=0 is a rating-time divisor → must be rejected.
        ("fixed_unit_price", {"unit_price_minor": 3, "per_quantity": "0"}),
        ("cost_plus_fixed", {"fixed_markup_minor": 5, "per_quantity": "0"}),
        (
            "included_quota_then_overage",
            {"included_quota": "1", "overage_unit_price_minor": 2, "per_quantity": "0"},
        ),
    ]:
        with pytest.raises(AppError):
            v(policy_type, params)


def test_negative_adjustment_reverses_cleanly():
    """R52[7,8,9]: a full-reversal adjustment (negative quantity) must produce
    the exact negative of the original charge for every policy type — so the
    two events net to zero. Previously minimum_fee flipped it positive, tiers
    fell back to base rate, and cost_plus_fixed added a spurious +1 markup
    block on the refund."""
    ci = rating.compute_internal_cost_minor
    f = rating.compute_billable_minor
    tiers = [{"min_qty": "0", "unit_cost": "0.01"}, {"min_qty": "10000", "unit_cost": "0.005"}]

    # [8] tiers: a -50000 reversal picks the SAME 0.005 tier as +50000 (by
    # magnitude), so internal cost is an exact negation.
    up = rating.apply_tiers(Decimal("0.01"), tiers, Decimal("50000"))
    un = rating.apply_tiers(Decimal("0.01"), tiers, Decimal("-50000"))
    assert up == un == Decimal("0.005")

    # [7] minimum_fee floors a real (positive) charge but must NOT flip a
    # negative reversal into a positive charge.
    pos = ci(Decimal("0.01"), Decimal("10000"), "USD", 50)
    neg = ci(Decimal("0.01"), Decimal("-10000"), "USD", 50)
    assert pos == 10000 and neg == -10000

    # [9] cost_plus_fixed: forward bills N markup blocks, reversal reverses
    # exactly N — no spurious +1 block on the refund.
    fwd = f(
        "cost_plus_fixed",
        {"fixed_markup_minor": 500, "per_quantity": "1000"},
        internal_cost_minor=10000,
        quantity=Decimal(1000),
    )
    rev = f(
        "cost_plus_fixed",
        {"fixed_markup_minor": 500, "per_quantity": "1000"},
        internal_cost_minor=-10000,
        quantity=Decimal(-1000),
    )
    assert fwd == 10500 and rev == -10500
    assert fwd + rev == 0

    # cost_plus_percentage nets to zero too.
    pf = f(
        "cost_plus_percentage",
        {"percentage": "20"},
        internal_cost_minor=10000,
        quantity=Decimal(10000),
    )
    rf = f(
        "cost_plus_percentage",
        {"percentage": "20"},
        internal_cost_minor=-10000,
        quantity=Decimal(-10000),
    )
    assert pf + rf == 0


# ── Cost ladder + effective dating ───────────────────────────


@pytest.mark.asyncio
async def test_cost_ladder_and_effective_boundary(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    t0 = datetime.now(UTC) - timedelta(days=30)
    t1 = datetime.now(UTC) - timedelta(days=10)
    # Old window [t0, t1): 0.02; new window [t1, ∞): 0.01
    await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="mock",
        model_or_service="mock-img",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.02"),
        effective_from=t0,
        effective_until=t1,
    )
    await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="mock",
        model_or_service="mock-img",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.01"),
        effective_from=t1,
    )
    # Event in the OLD window rates at the old price (point-in-time semantics)
    old_event = await _mk_event(
        db,
        tenant,
        provider="mock",
        model_or_service="mock-img",
        occurred_at=t1 - timedelta(seconds=1),
        quantity=100,
    )
    rated_old = await rating.rate_event(db, old_event.id)
    assert rated_old.internal_cost_minor == 200  # 0.02×100 = $2.00
    # Event exactly AT the boundary uses the new rate (half-open [from, until))
    new_event = await _mk_event(
        db,
        tenant,
        provider="mock",
        model_or_service="mock-img",
        occurred_at=t1,
        quantity=100,
    )
    rated_new = await rating.rate_event(db, new_event.id)
    assert rated_new.internal_cost_minor == 100
    assert rated_new.cost_rate_snapshot["resolution"] == "exact"


@pytest.mark.asyncio
async def test_no_rate_falls_to_zero_cost_but_still_bills(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    event = await _mk_event(db, tenant, provider="unknown-provider")
    rated = await rating.rate_event(db, event.id)
    assert rated.internal_cost_minor == 0
    assert rated.cost_rate_snapshot.get("no_rate") is True
    # Global cost+50% fallback on 0 cost = 0 billable, but rated (not blocked)
    assert rated.status == "rated"


# ── Policy specificity ───────────────────────────────────────


@pytest.mark.asyncio
async def test_specificity_tenant_beats_global(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"tenant-specific {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 7},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    event = await _mk_event(db, tenant, quantity=10)
    rated = await rating.rate_event(db, event.id)
    assert rated.sell_rate_snapshot["scope"] == "tenant"
    assert rated.billable_amount_minor == 70  # 7×10, not global cost+50%


@pytest.mark.asyncio
async def test_global_fallback_policy_applies(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="fallbackp",
        model_or_service="m1",
        usage_type="voice_generation",
        currency="USD",
        unit_cost=Decimal("0.01"),
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    event = await _mk_event(
        db,
        tenant,
        usage_type="voice_generation",
        provider="fallbackp",
        model_or_service="m1",
        quantity=100,
    )
    rated = await rating.rate_event(db, event.id)
    # 100×0.01 = $1.00 = 100 minor; +50% = 150
    assert rated.internal_cost_minor == 100
    assert rated.billable_amount_minor == 150
    assert rated.sell_rate_snapshot["scope"] == "global"


# ── FX blocking + unblocking ─────────────────────────────────


@pytest.mark.asyncio
async def test_fx_missing_blocks_then_unblocks(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, currency="CNY")
    # Tenant-specific USD policy → needs USD->CNY FX
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"usd-policy {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 10},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    event = await _mk_event(db, tenant, quantity=10)
    rated = await rating.rate_event(db, event.id)
    assert rated.status == "blocked"
    assert "USD->CNY" in rated.sell_rate_snapshot.get("fx_gaps", [])
    # Add the FX rate → retry (simulates the fx.rate_created handler)
    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="USD",
        quote_currency="CNY",
        rate=Decimal("7.12"),
        effective_from=datetime.now(UTC) - timedelta(days=2),
    )
    rated2 = await rating.rate_event(db, event.id)
    assert rated2.id == rated.id  # same row, updated in place
    assert rated2.status == "rated"
    # 10 images × 10 minor USD = 100 minor USD = $1.00 → ¥7.12 = 712 CNY minor
    assert rated2.billable_amount_minor == 712
    assert rated2.fx_rate_snapshot["rate"] == "7.12000000"


@pytest.mark.asyncio
async def test_cost_plus_bridges_cost_currency_to_policy_currency(db):
    """R52[6] CRITICAL: for cost_plus_* the internal cost is in the COST rate's
    currency, but billable is derived from it and then treated as the POLICY
    currency. When cost currency != policy currency, the number must be bridged
    (cost -> policy via FX) BEFORE the markup, else the markup is applied to raw
    cost-currency minor units and the whole chain mis-bills.

    Setup: cost rate in USD ($0.10/img), policy cost_plus_percentage 0% in JPY,
    tenant in JPY. USD->JPY = 150. 10 images → $1.00 cost → ¥150 (JPY minor
    mult 1) → +0% markup → ¥150 billable. The bug would treat the $1.00 = 100
    USD-minor as ¥100 and bill ¥100."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user, currency="JPY")
    await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="brg",
        model_or_service="m",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.10"),
        effective_from=datetime.now(UTC) - timedelta(days=2),
    )
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"jpy-costplus {ULID()}",
        policy_type="cost_plus_percentage",
        usage_type="image_generation",
        currency="JPY",
        params={"percentage": "0"},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="USD",
        quote_currency="JPY",
        rate=Decimal("150"),
        effective_from=datetime.now(UTC) - timedelta(days=2),
    )
    event = await _mk_event(db, tenant, provider="brg", model_or_service="m", quantity=10)
    rated = await rating.rate_event(db, event.id)
    assert rated.status == "rated"
    # $0.10 × 10 = $1.00 = 100 USD-minor internal; bridged ×150 → ¥150; +0% → 150.
    assert rated.internal_cost_minor == 100
    assert rated.internal_cost_currency == "USD"
    assert rated.billable_amount_minor == 150, rated.billable_amount_minor
    assert rated.billable_currency == "JPY"


@pytest.mark.asyncio
async def test_sub_half_minor_events_accumulate_not_round_to_zero(db):
    """R75 CRITICAL: fixed_unit_price $1.00 per 1M tokens. Each 4000-token event
    is worth 0.4 minor — the per-event rounded integer is 0, but the EXACT
    column carries 0.4. 250 such events (1M tokens) must bill 100 minor
    (round-of-sum), not 0 (sum-of-rounded)."""
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.services import metering, rating
    from app.controlplane.services import pricing as pricing_svc
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
        OrgStatus,
    )

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org = Organization(
        name="R75",
        slug=f"r75-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"submin {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="llm_input_tokens",
        currency="USD",
        params={"unit_price_minor": 100, "per_quantity": "1000000"},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    exacts = []
    for i in range(250):
        ev = await metering.emit_usage(
            db,
            tenant_id=tenant.id,
            org_id=org.id,
            usage_type="llm_input_tokens",
            quantity=4000,
            occurred_at=datetime.now(UTC),
            source="manual",
            idempotency_key=f"submin-{i}-{ULID()}",
        )
        r = await rating.rate_event(db, ev.id)
        exacts.append(r)
    # Each event's rounded integer is 0 (0.4 → 0) but exact is 0.4.
    assert all(r.billable_amount_minor == 0 for r in exacts)
    assert all(
        abs(Decimal(r.billable_amount_exact) - Decimal("0.4")) < Decimal("0.0001") for r in exacts
    )
    # Sum of exact = 250 × 0.4 = 100.0 minor.
    total_exact = sum(Decimal(r.billable_amount_exact) for r in exacts)
    assert total_exact == Decimal(100)
    # The invoice usage-line rounds the SUM once → 100, not sum-of-rounded 0.
    from sqlalchemy import func as _f

    invoice_amount = (
        await db.execute(
            select(_f.coalesce(_f.sum(RatedUsage.billable_amount_exact), 0)).where(
                RatedUsage.tenant_id == tenant.id
            )
        )
    ).scalar_one()
    assert int(Decimal(invoice_amount).quantize(Decimal("1"))) == 100


# ── Snapshot immutability (issue §13 acceptance) ─────────────


@pytest.mark.asyncio
async def test_margin_reproducible_after_catalog_changes(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    rate = await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="snapb",
        model_or_service="m2",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.018"),
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    event = await _mk_event(db, tenant, provider="snapb", model_or_service="m2", quantity=100)
    rated = await rating.rate_event(db, event.id)
    frozen = (
        rated.internal_cost_minor,
        rated.billable_amount_minor,
        rated.margin_minor,
        dict(rated.cost_rate_snapshot),
        dict(rated.sell_rate_snapshot),
    )
    # Supersede the rate with a much higher price
    await pricing_svc.supersede_cost_rate(
        db,
        rate,
        effective_until=datetime.now(UTC) + timedelta(seconds=1),
        successor={
            "unit_cost": Decimal("99"),
            "effective_from": datetime.now(UTC) + timedelta(seconds=1),
        },
        actor=_actor(user),
    )
    # Re-read: byte-identical
    await db.refresh(rated)
    assert (
        rated.internal_cost_minor,
        rated.billable_amount_minor,
        rated.margin_minor,
        dict(rated.cost_rate_snapshot),
        dict(rated.sell_rate_snapshot),
    ) == frozen
    # Re-rating is a no-op (idempotent)
    again = await rating.rate_event(db, event.id)
    assert again.id == rated.id


# ── Concurrency ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_concurrent_rating_single_row():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            event = await _mk_event(setup, tenant)
            await setup.commit()
            event_id = event.id

        async def rate_it():
            async with AsyncSessionLocal() as s:
                r = await rating.rate_event(s, event_id)
                await s.commit()
                return r.id if r else None

        ids = await asyncio.gather(*[rate_it() for _ in range(10)])
        async with AsyncSessionLocal() as s:
            rows = (
                (await s.execute(select(RatedUsage).where(RatedUsage.usage_event_id == event_id)))
                .scalars()
                .all()
            )
            assert len(rows) == 1
            assert all(i == rows[0].id for i in ids if i)
    finally:
        await engine.dispose()


# ── Void + immutability guards ───────────────────────────────


@pytest.mark.asyncio
async def test_void_and_invoiced_guard(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    event = await _mk_event(db, tenant)
    rated = await rating.rate_event(db, event.id)
    voided = await rating.void_rated(db, rated.id, reason="recon mismatch", actor=_actor(user))
    assert voided.status == "voided"
    # invoiced rows cannot be voided
    event2 = await _mk_event(db, tenant)
    rated2 = await rating.rate_event(db, event2.id)
    rated2.status = "invoiced"
    await db.flush()
    with pytest.raises(AppError) as exc:
        await rating.void_rated(db, rated2.id, reason="nope", actor=_actor(user))
    assert exc.value.code == "RATED_USAGE_INVOICED"


@pytest.mark.asyncio
async def test_cost_rate_overlap_rejected(db):
    user = await _mk_user(db)
    t0 = datetime.now(UTC) - timedelta(days=5)
    await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider="ovl",
        model_or_service="m",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.01"),
        effective_from=t0,
    )
    with pytest.raises(AppError) as exc:
        await pricing_svc.create_cost_rate(
            db,
            actor=_actor(user),
            provider="ovl",
            model_or_service="m",
            usage_type="image_generation",
            currency="USD",
            unit_cost=Decimal("0.02"),
            effective_from=t0 + timedelta(days=1),
        )
    assert exc.value.code == "COST_RATE_OVERLAP"


# ── Outbox integration ───────────────────────────────────────


@pytest.mark.asyncio
async def test_usage_recorded_handler_rates_via_outbox():
    from app.controlplane.worker import process_outbox_once
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as db:
            user = await _mk_user(db)
            tenant = await _mk_tenant(db, user)
            event = await _mk_event(db, tenant)
            await db.commit()
            event_id = event.id
        # The shared dev DB accumulates pending usage.recorded debris from
        # other test runs; one 50-row batch may not reach OUR message. Drain
        # in bounded batches until our event is rated (available_at ordering
        # guarantees progress toward it).
        rated = None
        for _ in range(80):
            async with AsyncSessionLocal() as db:
                handled = await process_outbox_once(db, topics=["usage.recorded"])
                await db.commit()
            async with AsyncSessionLocal() as db:
                rated = (
                    await db.execute(
                        select(RatedUsage).where(RatedUsage.usage_event_id == event_id)
                    )
                ).scalar_one_or_none()
                if rated is not None:
                    break
            if handled == 0:
                break
        assert rated is not None
        assert rated.status == "rated"
    finally:
        await engine.dispose()


# ── R61: FX lifecycle + unblock targeting ────────────────────


@pytest.mark.asyncio
async def test_fx_rate_supersede_open_ended(db):
    """R61[1]: an open-ended FX rate blocked every future rate for the pair
    forever (no supersede path). Creating a newer rate now auto-closes the
    live open-ended window at the new effective_from; point-in-time reads
    still resolve the old rate for old timestamps."""
    user = await _mk_user(db)
    pair = dict(base_currency="USD", quote_currency="SEK")
    old_rate = await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        rate=Decimal("10.5"),
        effective_from=datetime.now(UTC) - timedelta(days=30),
        **pair,
    )
    assert old_rate.effective_until is None
    cutover = datetime.now(UTC) - timedelta(days=1)
    new_rate = await pricing_svc.create_fx_rate(
        db, actor=_actor(user), rate=Decimal("11.2"), effective_from=cutover, **pair
    )
    await db.refresh(old_rate)
    assert old_rate.effective_until == cutover  # auto-closed
    # Point-in-time: 10 days ago → old rate; now → new rate
    r_old, snap_old = await rating.resolve_fx(
        db, "USD", "SEK", datetime.now(UTC) - timedelta(days=10)
    )
    assert snap_old["fx_rate_id"] == old_rate.id
    r_new, snap_new = await rating.resolve_fx(db, "USD", "SEK", datetime.now(UTC))
    assert snap_new["fx_rate_id"] == new_rate.id
    # A BACKDATED overlapping window is still rejected (history immutable)
    with pytest.raises(AppError) as exc:
        await pricing_svc.create_fx_rate(
            db,
            actor=_actor(user),
            rate=Decimal("9"),
            effective_from=datetime.now(UTC) - timedelta(days=10),
            effective_until=datetime.now(UTC) - timedelta(days=5),
            **pair,
        )
    assert exc.value.code == "FX_RATE_OVERLAP"


@pytest.mark.asyncio
async def test_inverse_fx_zero_guard(db):
    """R61[3]: a hyperinflated stored rate inverts to Decimal 0 at 8dp — a
    zero rate silently made every conversion free. Unrepresentable inverse
    must resolve as 'no rate' (row blocks) instead."""
    user = await _mk_user(db)
    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="USD",
        quote_currency="VES",
        rate=Decimal("300000000"),
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    # Forward still works
    fwd = await rating.resolve_fx(db, "USD", "VES", datetime.now(UTC))
    assert fwd is not None and fwd[0] == Decimal("300000000")
    # Inverse would quantize to 0 → treated as missing
    inv = await rating.resolve_fx(db, "VES", "USD", datetime.now(UTC))
    assert inv is None
    # Sanity: a representable inverse still resolves
    await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="USD",
        quote_currency="NOK",
        rate=Decimal("10"),
        effective_from=datetime.now(UTC) - timedelta(days=1),
    )
    inv2 = await rating.resolve_fx(db, "NOK", "USD", datetime.now(UTC))
    assert inv2 is not None and inv2[0] == Decimal("0.1")


@pytest.mark.asyncio
async def test_fx_unblock_targets_created_pair(db):
    """R61[2]: the fx.rate_created handler retried 500 ARBITRARY blocked rows
    (no pair filter/order/continuation) — the rows the new rate would fix
    could be starved forever behind unfixable ones. The handler now filters
    on the recorded fx_gap of the created pair and pages through all of it."""
    user = await _mk_user(db)
    # Tenant billed in CZK; two policies price in HUF and PLN → two gap kinds
    tenant = await _mk_tenant(db, user, currency="CZK")
    for cur in ("HUF", "PLN"):
        await pricing_svc.create_price_policy(
            db,
            actor=_actor(user),
            name=f"p-{cur} {ULID()}",
            policy_type="fixed_unit_price",
            usage_type="image_generation" if cur == "HUF" else "voice_generation",
            currency=cur,
            params={"unit_price_minor": 10},
            effective_from=datetime.now(UTC) - timedelta(days=1),
            tenant_id=tenant.id,
        )
    ev_fixable = await _mk_event(db, tenant, usage_type="image_generation", quantity=1)
    ev_unfixable = await _mk_event(db, tenant, usage_type="voice_generation", quantity=1)
    r1 = await rating.rate_event(db, ev_fixable.id)
    r2 = await rating.rate_event(db, ev_unfixable.id)
    assert r1.status == "blocked" and "HUF->CZK" in r1.sell_rate_snapshot["fx_gaps"]
    assert r2.status == "blocked" and "PLN->CZK" in r2.sell_rate_snapshot["fx_gaps"]
    # Create ONLY the HUF->CZK rate and drive the handler with its id
    fx = await pricing_svc.create_fx_rate(
        db,
        actor=_actor(user),
        base_currency="HUF",
        quote_currency="CZK",
        rate=Decimal("0.06"),
        effective_from=datetime.now(UTC) - timedelta(days=2),
    )
    # Record WHICH rows the handler retries — the starvation failure mode is
    # "the fixable row never gets picked because unrelated rows fill the
    # batch", so the pair filter must retry ONLY pair-matched rows.
    retried: list[str] = []
    real_rate_event = rating.rate_event

    async def recording_rate_event(db_, event_id):
        retried.append(event_id)
        return await real_rate_event(db_, event_id)

    rating.rate_event = recording_rate_event
    try:
        await rating._handle_fx_created(db, {"fx_rate_id": fx.id})
    finally:
        rating.rate_event = real_rate_event
    await db.refresh(r1)
    await db.refresh(r2)
    assert r1.status == "rated", "the fixable pair-matched row must unblock"
    assert r2.status == "blocked", "unrelated pair must not be touched"
    assert ev_fixable.id in retried
    assert ev_unfixable.id not in retried, (
        "handler must target the created pair, not sweep arbitrary blocked rows"
    )


@pytest.mark.asyncio
async def test_reconciliation_cost_scoped_to_report_currency(db):
    """R61[4]: platform_cost summed internal_cost_minor across rows in MIXED
    internal_cost_currency (a superseding EUR cost rate mid-month splits the
    rows) and diffed the polluted sum against a single-currency provider
    figure. Cost now aggregates only rows in the report's currency; foreign-
    currency rows are surfaced as a count."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token
    from app.main import app

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    provider = f"rcn{str(ULID()).lower()[-6:]}"
    # USD cost rate then EUR successor — one event rated under each
    # Anchor both events INSIDE one calendar month (the report period) with
    # the currency cutover between them.
    t0 = datetime.now(UTC) - timedelta(hours=3)
    if (t0 + timedelta(hours=2)).month != t0.month:
        t0 -= timedelta(hours=3)  # avoid straddling a month boundary
    cutover = t0 + timedelta(hours=1)
    usd_rate = await pricing_svc.create_cost_rate(
        db,
        actor=_actor(user),
        provider=provider,
        model_or_service="m",
        usage_type="image_generation",
        currency="USD",
        unit_cost=Decimal("0.10"),
        effective_from=t0 - timedelta(days=10),
    )
    await pricing_svc.supersede_cost_rate(
        db,
        usd_rate,
        effective_until=cutover,
        successor={"currency": "EUR", "unit_cost": Decimal("0.09")},
        actor=_actor(user),
    )
    ev_usd = await _mk_event(
        db,
        tenant,
        provider=provider,
        model_or_service="m",
        quantity=10,
        occurred_at=t0,
    )
    ev_eur = await _mk_event(
        db,
        tenant,
        provider=provider,
        model_or_service="m",
        quantity=10,
        occurred_at=cutover + timedelta(hours=1),
    )
    r_usd = await rating.rate_event(db, ev_usd.id)
    r_eur = await rating.rate_event(db, ev_eur.id)
    assert r_usd.internal_cost_currency == "USD" and r_usd.internal_cost_minor == 100
    assert r_eur.internal_cost_currency == "EUR" and r_eur.internal_cost_minor == 90

    admin = await _mk_user(db)
    db.add(PlatformRoleAssignment(user_id=admin.id, role="billing_admin"))
    await db.commit()
    token = create_access_token(admin.id, admin.email, admin.role.value)
    period = t0.strftime("%Y-%m")

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            r = await c.post(
                "/api/v1/platform/reconciliation/reports",
                json={
                    "provider": provider,
                    "usage_type": "image_generation",
                    "period": period,
                    "provider_reported_quantity": "20",
                    "provider_reported_cost_minor": 100,
                    "currency": "USD",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
            assert r.status_code == 201, r.text
            data = r.json()["data"]
            # Cost: ONLY the USD row (100), not USD+EUR (190)
            assert int(data["platform_cost_minor"]) == 100
            assert int(data["delta_cost_minor"]) == 0
            assert int(data["other_currency_rows"]) == 1
    finally:
        app.router.lifespan_context = orig
        await db.rollback()
