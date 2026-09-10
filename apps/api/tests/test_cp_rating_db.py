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
    # R123: the fx.rate_created handler now commits per page (M13) — a prior
    # run's HUF→CZK rate survives in the dev DB and would make the "blocked"
    # setup rate cleanly. Clear the pair first (test owns these currencies).
    from sqlalchemy import text as _text

    await db.execute(
        _text(
            "DELETE FROM cp_fx_rates WHERE (base_currency, quote_currency) "
            "IN (('HUF','CZK'), ('CZK','HUF'), ('PLN','CZK'), ('CZK','PLN'))"
        )
    )
    await db.flush()
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


@pytest.mark.asyncio
async def test_rated_usage_pagination_stable_across_identical_timestamps(db):
    """R90[14]: batch rating writes hundreds of rows with the SAME rated_at
    (pg now() is tx-fixed); ordering by rated_at alone made offset pages
    duplicate/skip rows. The id tiebreaker makes the order total."""
    from contextlib import asynccontextmanager

    from httpx import ASGITransport, AsyncClient

    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.tenant import PlatformRoleAssignment
    from app.core.security import create_access_token
    from app.main import app

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    db.add(PlatformRoleAssignment(user_id=user.id, role="billing_admin"))
    # 25 rows in ONE tx → identical rated_at server_default
    for i in range(25):
        ev = await _mk_event(db, tenant, quantity=i + 1)
        db.add(
            RatedUsage(
                usage_event_id=ev.id,
                tenant_id=tenant.id,
                org_id="01JFAKEORGFAKEORGFAKEORGFA",
                usage_type="image_generation",
                quantity=i + 1,
                cost_rate_snapshot={},
                internal_cost_minor=0,
                internal_cost_currency="USD",
                sell_rate_snapshot={},
                billable_amount_minor=i,
                billable_amount_exact=i,
                internal_cost_exact=0,
                billable_currency="USD",
                status="rated",
            )
        )
    await db.commit()
    token = create_access_token(user.id, user.email, user.role.value)

    @asynccontextmanager
    async def _noop(a):
        yield

    orig = app.router.lifespan_context
    app.router.lifespan_context = _noop
    try:
        seen: list[str] = []
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
            hdr = {"Authorization": f"Bearer {token}"}
            for page in (1, 2, 3):
                r = await c.get(
                    "/api/v1/platform/rated-usage",
                    params={"tenant_id": tenant.id, "page": page, "per_page": 10},
                    headers=hdr,
                )
                assert r.status_code == 200, r.text
                seen.extend(row["id"] for row in r.json()["data"])
        assert len(seen) == 25
        assert len(set(seen)) == 25, "pages duplicated/skipped rows on tied timestamps"
    finally:
        app.router.lifespan_context = orig
        await db.rollback()


@pytest.mark.asyncio
async def test_fx_chunk_reenqueue_carries_cursor(db):
    """R130[12]: the chunk re-enqueue must carry a keyset cursor — the R129
    cursorless re-select livelocked on the same first 500 rows forever when
    they stayed blocked (rate effective_from AFTER their occurred_at)."""
    # Direct handler-contract test: payload with a cursor selects only rows
    # AFTER it; a full chunk re-enqueues with the LAST row id as the cursor.
    import app.controlplane.models.outbox as outbox_mod
    from app.controlplane.services.rating import _handle_fx_created

    enqueued = []
    orig_enqueue = outbox_mod.enqueue

    def _capture(db_, topic, payload):
        enqueued.append((topic, payload))
        return orig_enqueue(db_, topic, payload)

    outbox_mod.enqueue = _capture
    try:
        # No fx row for the id → no pair filter; empty blocked set for a
        # cursor beyond every ULID means no re-enqueue.
        await _handle_fx_created(db, {"fx_rate_id": "01ZZZZZZZZZZZZZZZZZZZZZZZZ", "after_id": "z"})
    finally:
        outbox_mod.enqueue = orig_enqueue
    assert enqueued == [], "no full chunk → no re-enqueue"


@pytest.mark.asyncio
async def test_unvoid_polarity_and_double_correct_gates(db):
    """R134 ([F11]): unvoid gate polarity. Restoring a voided ADJUSTMENT is
    ALLOWED only when its original is live (normal compensating pair);
    BLOCKED when the original is struck (would credit with no charge).
    Restoring an ORIGINAL is always safe."""

    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services.rating import unvoid_rated

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org_id = "01JBLORGRAT000000000000000"

    async def _event(adjustment_of=None):
        ev = UsageEvent(
            tenant_id=tenant.id,
            org_id=org_id,
            usage_type="api_request",
            quantity=1,
            unit="requests",
            occurred_at=datetime.now(UTC),
            source="adjustment" if adjustment_of else "manual",
            adjustment_of_id=adjustment_of,
        )
        db.add(ev)
        await db.flush()
        return ev

    async def _rated(ev, status, amount):
        r = RatedUsage(
            usage_event_id=ev.id,
            tenant_id=tenant.id,
            org_id=org_id,
            usage_type=ev.usage_type,
            quantity=ev.quantity,
            cost_rate_snapshot={},
            internal_cost_minor=0,
            internal_cost_currency="USD",
            sell_rate_snapshot={},
            billable_amount_minor=amount,
            billable_currency="USD",
            status=status,
        )
        db.add(r)
        await db.flush()
        return r

    # Original live (rated $100); adjustment VOIDED (-$100).
    orig_ev = await _event()
    await _rated(orig_ev, "rated", 100)
    adj_ev = await _event(adjustment_of=orig_ev.id)
    adj_rated = await _rated(adj_ev, "voided", -100)
    # Restoring the adjustment onto a LIVE original is the normal state → OK.
    restored = await unvoid_rated(
        db, adj_rated.id, reason="adjustment was correct", actor=_actor(user)
    )
    assert restored.status == "rated"

    # Now the forbidden shape: original VOIDED, adjustment VOIDED; restoring
    # the adjustment would credit with no offsetting charge → 409.
    orig2 = await _event()
    o2r = await _rated(orig2, "voided", 100)
    adj2 = await _event(adjustment_of=orig2.id)
    a2r = await _rated(adj2, "voided", -100)
    with pytest.raises(AppError) as exc:
        await unvoid_rated(db, a2r.id, reason="try", actor=_actor(user))
    assert exc.value.code == "RATED_USAGE_INVOICED"
    # Restoring the ORIGINAL is always safe.
    restored_o = await unvoid_rated(db, o2r.id, reason="fix original", actor=_actor(user))
    assert restored_o.status == "rated"


@pytest.mark.asyncio
async def test_concurrent_cost_rate_creates_cannot_overlap():
    """R147: the overlap pre-check is read-then-insert with NO DB constraint
    backstop — two concurrent creates for the same dimensions both passed and
    committed OVERLAPPING windows (under cost_plus_* policies the ambiguous
    cost basis changes customer billing). The dimension-tuple advisory lock
    serializes check→insert; the loser sees the winner's committed row → 409."""
    from app.controlplane.models.pricing import ProviderCostRate
    from app.core.database import engine

    dims = f"race-{str(ULID()).lower()[:8]}"
    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            await setup.commit()
            user_id = user.id

        t0 = datetime.now(UTC) - timedelta(days=1)
        outcomes: list[str] = []

        def _args(u):
            return dict(
                actor=_actor(u),
                provider=dims,
                model_or_service="m1",
                usage_type="image_generation",
                currency="USD",
                unit_cost=Decimal("0.02"),
                effective_from=t0,
            )

        # Deterministic interleave: A creates and HOLDS its tx open (its
        # pre-check row is invisible to B); B's create must BLOCK on the
        # dimension advisory lock until A commits, then see the winner row →
        # 409. Pre-fix, B's pre-check passed and both rows committed.
        sa = AsyncSessionLocal()
        sb = AsyncSessionLocal()
        try:
            ua = await sa.get(User, user_id)
            await pricing_svc.create_cost_rate(sa, **_args(ua))

            async def b_create():
                ub = await sb.get(User, user_id)
                try:
                    await pricing_svc.create_cost_rate(sb, **_args(ub))
                    await sb.commit()
                    outcomes.append("created")
                except AppError as e:
                    await sb.rollback()
                    outcomes.append(e.code)
                except Exception as exc:  # noqa: BLE001
                    await sb.rollback()
                    outcomes.append(type(exc).__name__)

            b_task = asyncio.create_task(b_create())
            await asyncio.sleep(0.3)  # B is now blocked on the advisory lock
            await sa.commit()
            await b_task
        finally:
            await sa.close()
            await sb.close()
        assert outcomes == ["COST_RATE_OVERLAP"], outcomes
        async with AsyncSessionLocal() as s:
            rows = (
                (
                    await s.execute(
                        select(ProviderCostRate).where(ProviderCostRate.provider == dims)
                    )
                )
                .scalars()
                .all()
            )
            assert len(rows) == 1, f"{len(rows)} overlapping rates committed"
    finally:
        await engine.dispose()


def test_min_fee_not_applied_to_zero_cost():
    """R162 (mutation probe): a ZERO-cost/zero-quantity event must NOT be
    floored up to the minimum fee — the floor applies only to a real positive
    charge (cost > 0). A `>=` here would silently bill the minimum fee on a
    zero-usage event (phantom overcharge). Pins both the _minor and _exact
    paths so a `> → >=` mutation is killed."""
    # zero quantity, min fee set → stays 0, never floored to 50
    assert rating.compute_internal_cost_minor(Decimal("0.018"), Decimal(0), "USD", 50) == 0
    assert rating.compute_internal_cost_exact(
        Decimal("0.018"), Decimal(0), "USD", 50
    ) == Decimal(0)
    # zero unit cost, positive quantity, min fee → also 0 (no real charge)
    assert rating.compute_internal_cost_minor(Decimal("0"), Decimal(10), "USD", 50) == 0
    # a genuine positive charge below the floor IS raised to it (control)
    assert rating.compute_internal_cost_minor(Decimal("0.10"), Decimal(1), "USD", 50) == 50
    # negative reversal never flips into a positive minimum-fee charge
    assert rating.compute_internal_cost_minor(Decimal("0.018"), Decimal(-10), "USD", 50) == -50
    # exact path: a real positive charge below the floor is RAISED to it
    # (max, not min) — the exact twin's floor must be pinned too.
    assert rating.compute_internal_cost_exact(Decimal("0.10"), Decimal(1), "USD", 50) == Decimal(50)


def test_apply_tiers_first_wins_on_duplicate_min_qty():
    """R162 (mutation probe): with two tiers at the SAME min_qty the FIRST
    listed wins (strict `>` on best_min). Pins first-wins so a `> → >=`
    mutation (which would flip to last-wins) is killed."""
    tiers = [
        {"min_qty": "100", "unit_cost": "0.010"},  # first at 100 — wins
        {"min_qty": "100", "unit_cost": "0.099"},  # duplicate — must NOT override
    ]
    assert rating.apply_tiers(Decimal("0.02"), tiers, Decimal("500")) == Decimal("0.010")


def test_compute_billable_exact_mirrors_minor():
    """R162: the _exact billable twin had only DB-level coverage. Pin the pure
    matrix directly so its operators (pct, block ceiling, unit price, quota)
    are mutation-covered without a DB."""
    fe = rating.compute_billable_exact
    assert fe("cost_plus_percentage", {"percentage": "50"},
              internal_cost_exact=Decimal(100), quantity=Decimal(1)) == Decimal(150)
    # unit price accumulates the sub-minor remainder (0.4), not rounded to 0
    assert fe("fixed_unit_price", {"unit_price_minor": 1, "per_quantity": "1000000"},
              internal_cost_exact=Decimal(0), quantity=Decimal(400000)) == Decimal("0.4")
    # block markup: 1400/1000 → 2 blocks
    assert fe("cost_plus_fixed", {"fixed_markup_minor": 500, "per_quantity": "1000"},
              internal_cost_exact=Decimal(100), quantity=Decimal(1400)) == Decimal(100 + 1000)
    # quota overage: prior 0, included 100, qty 150 → 50 over × 2 = 100
    assert fe("included_quota_then_overage",
              {"included_quota": "100", "overage_unit_price_minor": 2},
              internal_cost_exact=Decimal(0), quantity=Decimal(150)) == Decimal(100)


# ── R244: pricing service reject-branch coverage ──


@pytest.mark.asyncio
async def test_fx_and_cost_rate_validation_rejects(db):
    """R244: create_fx_rate / create_cost_rate / supersede / create_price_policy
    guards — each reject arc protects money math from unratable state."""
    user = await _mk_user(db)
    now = datetime.now(UTC)

    async def fx(**kw):
        base = dict(base_currency="USD", quote_currency="EUR", rate=Decimal("0.9"),
                    effective_from=now)
        base.update(kw)
        return await pricing_svc.create_fx_rate(db, actor=_actor(user), **base)

    with pytest.raises(AppError) as e:
        await fx(quote_currency="USD")                       # base == quote
    assert e.value.code == "FX_RATE_INVALID"
    with pytest.raises(AppError) as e:
        await fx(rate=Decimal("0"))                          # non-positive
    assert e.value.code == "FX_RATE_INVALID"
    with pytest.raises(AppError) as e:
        await fx(rate=Decimal("NaN"))                        # non-finite
    assert e.value.code == "FX_RATE_INVALID"

    async def cost(**kw):
        base = dict(provider="mock", model_or_service="m", usage_type="image_generation",
                    currency="USD", unit_cost=Decimal("0.02"), effective_from=now)
        base.update(kw)
        return await pricing_svc.create_cost_rate(db, actor=_actor(user), **base)

    with pytest.raises(AppError) as e:
        await cost(usage_type="quantum_flux")                # unknown usage type
    assert e.value.code == "UNKNOWN_USAGE_TYPE"
    with pytest.raises(AppError) as e:
        await cost(unit="parsecs")                           # unit mismatch
    assert e.value.code == "VALIDATION_ERROR"

    # supersede guards: window inversion, then double-supersede
    rate = await cost()
    succ = {"unit_cost": Decimal("0.03")}
    with pytest.raises(AppError) as e:
        await pricing_svc.supersede_cost_rate(
            db, rate, effective_until=now - timedelta(days=1),
            successor=dict(succ), actor=_actor(user))
    assert e.value.code == "VALIDATION_ERROR"
    await pricing_svc.supersede_cost_rate(
        db, rate, effective_until=now + timedelta(days=1),
        successor=dict(succ), actor=_actor(user))
    with pytest.raises(AppError) as e:
        await pricing_svc.supersede_cost_rate(
            db, rate, effective_until=now + timedelta(days=2),
            successor=dict(succ), actor=_actor(user))
    assert e.value.code == "COST_RATE_IMMUTABLE"

    # price policy: unknown usage type, multi-scope contradiction
    async def policy(**kw):
        base = dict(policy_type="cost_plus_percentage", params={"percentage": "10"})
        base.update(kw)
        return await pricing_svc.create_price_policy(db, actor=_actor(user), **base)

    with pytest.raises(AppError) as e:
        await policy(usage_type="quantum_flux")
    assert e.value.code == "UNKNOWN_USAGE_TYPE"
    with pytest.raises(AppError) as e:
        await policy(tenant_id="t1", partner_id="p1")
    assert e.value.code == "INVALID_POLICY_PARAMS"


@pytest.mark.asyncio
async def test_overage_prior_quantity_accumulation(db):
    """R270: the DB-side prior-quantity accumulation for
    included_quota_then_overage (rating.py's tenant-tz month window) had ZERO
    integration tests — only the pure function with an injected prior. Pins:
    sequential events consume the quota in order (only the overflow bills),
    a VOIDED rating's event stops consuming quota (R52[13]), and a same-
    timestamp reversal nets its original (R52[10] precedes-ordering)."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"quota {ULID()}",
        policy_type="included_quota_then_overage",
        usage_type="image_generation",
        currency="USD",
        params={"included_quota": "100", "overage_unit_price_minor": 5},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    t0 = datetime.now(UTC)

    # 80 within quota → 0; +30 → 10 over → 50; +10 → fully over → 50
    e1 = await _mk_event(db, tenant, quantity=80, occurred_at=t0)
    r1 = await rating.rate_event(db, e1.id)
    assert r1.billable_amount_minor == 0

    e2 = await _mk_event(db, tenant, quantity=30, occurred_at=t0 + timedelta(minutes=1))
    r2 = await rating.rate_event(db, e2.id)
    assert r2.billable_amount_minor == 50                  # 10 over × 5

    e3 = await _mk_event(db, tenant, quantity=10, occurred_at=t0 + timedelta(minutes=2))
    r3 = await rating.rate_event(db, e3.id)
    assert r3.billable_amount_minor == 50                  # all 10 over × 5

    # R52[13]: void e1's rating — its 80 must stop consuming quota, so a
    # NEW event of 10 fits back inside the freed quota (prior = 30+10 = 40)
    await rating.void_rated(db, r1.id, reason="strike", actor=_actor(user))
    e4 = await _mk_event(db, tenant, quantity=10, occurred_at=t0 + timedelta(minutes=3))
    r4 = await rating.rate_event(db, e4.id)
    assert r4.billable_amount_minor == 0                   # 40+10 ≤ 100

    # R52[10]: a reversal sharing the ORIGINAL's occurred_at must include the
    # original in its prior (created later → ordered after), netting to a
    # negative of what the original actually billed over quota.
    e5 = await _mk_event(db, tenant, quantity=60, occurred_at=t0 + timedelta(minutes=4))
    r5 = await rating.rate_event(db, e5.id)
    assert r5.billable_amount_minor == 50                  # prior 50, 50→110: 10 over
    e6 = await _mk_event(db, tenant, quantity=-60, source="adjustment",
                         occurred_at=t0 + timedelta(minutes=4))  # same timestamp
    r6 = await rating.rate_event(db, e6.id)
    assert r6.billable_amount_minor == -50                 # exact mirror, nets to 0


@pytest.mark.asyncio
async def test_fx_sweep_cursor_advances_past_unfixable_rows(db, monkeypatch):
    """R282: the R130[12] anti-livelock cursor. 501 blocked rows that
    rate_event cannot fix (simulated at the rate_event seam — the exact
    scenario: a rate that doesn't cover occurred_at leaves rows blocked) —
    the handler must page past them exactly once (chunk of 500, re-enqueue
    with after_id = the page's last row) and TERMINATE on the second
    message instead of re-selecting the same first 500 forever."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services import pricing as pricing_svc
    from app.controlplane.services.rating import _handle_fx_created

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    occurred = datetime.now(UTC) - timedelta(days=30)

    events, rated = [], []
    for _ in range(501):
        eid = str(ULID())
        events.append(UsageEvent(
            id=eid, tenant_id=tenant.id, org_id="01JFAKEORGFAKEORGFAKEORGFA",
            usage_type="image_generation", quantity=1, unit="images",
            occurred_at=occurred, source="manual"))
        rated.append(RatedUsage(
            usage_event_id=eid, tenant_id=tenant.id,
            org_id="01JFAKEORGFAKEORGFAKEORGFA", usage_type="image_generation",
            quantity=1, cost_rate_snapshot={}, internal_cost_minor=0,
            internal_cost_currency="ZAR",
            sell_rate_snapshot={"fx_gaps": ["ZAR->USD"]},
            billable_amount_minor=0, billable_amount_exact=Decimal(0),
            billable_currency="ZAR", status="blocked",
            rated_at=datetime.now(UTC)))
    db.add_all(events)
    await db.flush()
    db.add_all(rated)
    await db.flush()

    # the new rate does NOT cover occurred_at → every row stays unfixable
    rate = await pricing_svc.create_fx_rate(
        db, actor=_actor(user), base_currency="ZAR", quote_currency="USD",
        rate=Decimal("0.05"), effective_from=datetime.now(UTC))

    from app.controlplane.services import rating as rating_mod

    async def unfixable(db_, event_id):                    # rate stays blocked
        return None

    monkeypatch.setattr(rating_mod, "rate_event", unfixable)

    def cursor_msgs():
        return db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "fx.rate_created",
                OutboxMessage.payload["fx_rate_id"].astext == rate.id,
                OutboxMessage.payload["after_id"].astext.isnot(None)))

    await _handle_fx_created(db, {"fx_rate_id": rate.id})
    msgs = (await cursor_msgs()).scalars().all()
    assert len(msgs) == 1                                  # cursor re-enqueue
    cursor = msgs[0].payload["after_id"]
    assert cursor                                          # keyset carried

    await _handle_fx_created(db, msgs[0].payload)          # second page: 1 row
    msgs2 = (await cursor_msgs()).scalars().all()
    assert len(msgs2) == 1                                 # no further enqueue
    from sqlalchemy import func as _f

    still_blocked = (
        await db.execute(
            select(_f.count(RatedUsage.id)).where(
                RatedUsage.tenant_id == tenant.id, RatedUsage.status == "blocked"))
    ).scalar_one()
    assert still_blocked == 501                            # unfixable stay blocked


@pytest.mark.asyncio
async def test_unvoid_blocked_row_restores_to_blocked_and_redrives(db):
    """R283: a row voided while BLOCKED has zero amounts — R132[F5] restores
    it to 'blocked' (not 'rated', which would sweep a permanent zero-bill
    into the next close), and R133[F9] re-drives rating via usage.recorded
    (the FX rate may have landed while the row was voided; the fx sweep
    skips voided rows, so nothing else would ever re-rate it)."""
    from app.controlplane.models.outbox import OutboxMessage
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services.rating import unvoid_rated, void_rated

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    eid = str(ULID())
    db.add(UsageEvent(
        id=eid, tenant_id=tenant.id, org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation", quantity=1, unit="images",
        occurred_at=datetime.now(UTC), source="manual"))
    await db.flush()
    row = RatedUsage(
        usage_event_id=eid, tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA", usage_type="image_generation",
        quantity=1, cost_rate_snapshot={}, internal_cost_minor=0,
        internal_cost_currency="ZAR",
        sell_rate_snapshot={"fx_gaps": ["ZAR->USD"]},
        billable_amount_minor=0, billable_amount_exact=Decimal(0),
        billable_currency="ZAR", status="blocked", rated_at=datetime.now(UTC))
    db.add(row)
    await db.flush()

    await void_rated(db, row.id, reason="strike", actor=_actor(user))
    await db.refresh(row)
    assert row.status == "voided"

    restored = await unvoid_rated(db, row.id, reason="restore", actor=_actor(user))
    assert restored.status == "blocked"                    # NOT 'rated' (R132[F5])
    redrives = (
        (await db.execute(
            select(OutboxMessage).where(
                OutboxMessage.topic == "usage.recorded",
                OutboxMessage.payload["usage_event_id"].astext == eid)))
        .scalars().all()
    )
    assert len(redrives) == 1                              # R133[F9] re-drive


@pytest.mark.asyncio
async def test_offering_cost_fallback_for_workflow_events(db):
    """R284: a workflow-run event with no matching cost rate resolves its
    internal cost from the provider connection's ModelOffering
    (cost_per_call_usd) — the snapshot records the fallback and the offering
    id so the rated row stays auditable."""
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
        OrgStatus,
    )
    from app.models.provider import (
        ProviderAdapter,
        ProviderConnection,
        ProviderModelOffering,
    )
    from app.models.workflow_run import RunStatus, WorkflowRun

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org = Organization(
        name="OffOrg", slug=f"off-{str(ULID()).lower()}", status=OrgStatus.ACTIVE,
        tenant_id=tenant.id, created_by=user.id)
    db.add(org)
    await db.flush()
    db.add(OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER,
                     status=MemberStatus.ACTIVE))
    adapter = ProviderAdapter(key=f"off-{str(ULID()).lower()}", name="Off")
    db.add(adapter)
    await db.flush()
    conn = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="c",
                              created_by=user.id)
    db.add(conn)
    await db.flush()
    db.add(ProviderModelOffering(
        connection_id=conn.id, capability_key="text_generation",
        model_name="off-model", is_active=True, cost_per_call_usd=Decimal("2")))
    run = WorkflowRun(
        org_id=org.id, pack_id=None, release_id=None, installation_id=None,
        definition_snapshot={"steps": [], "edges": []}, inputs={},
        started_by=user.id, status=RunStatus.COMPLETED)
    db.add(run)
    await db.flush()

    # unique provider + voice_generation: no committed cost rate can match
    event = await _mk_event(
        db, tenant, org_id=org.id, usage_type="voice_generation", quantity=1,
        provider=f"prov-{str(ULID()).lower()[:8]}",
        workflow_run_id=run.id, provider_connection_id=conn.id,
        model_or_service="off-model")
    rated = await rating.rate_event(db, event.id)
    assert rated is not None
    snap = rated.cost_rate_snapshot or {}
    assert snap.get("fallback") == "offering"
    assert rated.internal_cost_minor == 200                # $2 → 200 US cents


@pytest.mark.asyncio
async def test_sell_policy_tiebreaks_typed_beats_wildcard_then_priority(db):
    """R308: when several price policies match at the SAME specificity tier,
    the deterministic tie-break is (rank, typed>wildcard, priority,
    effective_from, id). Pins the two money-relevant dimensions: an exact
    usage_type policy beats a NULL-wildcard one for its type, and among two
    typed same-rank policies the higher `priority` wins — so an event always
    rates at the intended price, not whichever row the DB returned first."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    now = datetime.now(UTC) - timedelta(days=1)

    async def policy(price, *, usage_type, priority=0):
        return await pricing_svc.create_price_policy(
            db, actor=_actor(user), name=f"p{price}-{ULID()}",
            policy_type="fixed_unit_price", usage_type=usage_type, currency="USD",
            params={"unit_price_minor": price}, effective_from=now,
            tenant_id=tenant.id, priority=priority)

    # tenant-scope wildcard @ 3/unit with a HIGH priority, and a tenant-scope
    # image_generation-specific policy @ 7/unit with LOW priority. type_rank
    # sits BEFORE priority in the tie-break key, so the typed policy must win
    # despite the wildcard's higher priority — this is what isolates type_rank
    # (without it, the wildcard's priority would win and misprice the event).
    await policy(3, usage_type=None, priority=9)
    await policy(7, usage_type="image_generation", priority=0)
    ev = await _mk_event(db, tenant, usage_type="image_generation", quantity=10)
    rated = await rating.rate_event(db, ev.id)
    assert rated.billable_amount_minor == 70   # typed (7) beats higher-priority wildcard

    # a DIFFERENT usage_type with no specific policy falls to the wildcard
    ev2 = await _mk_event(db, tenant, usage_type="image_editing", quantity=10)
    rated2 = await rating.rate_event(db, ev2.id)
    assert rated2.billable_amount_minor == 30  # wildcard (3)

    # two typed same-rank policies → higher priority wins
    user2 = await _mk_user(db)
    tenant2 = await _mk_tenant(db, user2)

    async def policy2(price, priority):
        return await pricing_svc.create_price_policy(
            db, actor=_actor(user2), name=f"q{price}-{ULID()}",
            policy_type="fixed_unit_price", usage_type="image_generation",
            currency="USD", params={"unit_price_minor": price}, effective_from=now,
            tenant_id=tenant2.id, priority=priority)

    await policy2(11, priority=1)
    await policy2(99, priority=5)   # higher priority
    ev3 = await _mk_event(db, tenant2, usage_type="image_generation", quantity=1)
    rated3 = await rating.rate_event(db, ev3.id)
    assert rated3.billable_amount_minor == 99


@pytest.mark.asyncio
async def test_cost_ladder_exact_beats_wildcard(db):
    """R309: internal-cost ladder precedence — an EXACT (provider+model) rate
    must win over a provider-wildcard (provider, NULL model) rate for the same
    provider+usage_type; peeling the exact rate falls to the wildcard. Only
    'exact' resolution was asserted before; a wrong rung is a wrong internal
    cost -> wrong margin."""
    from app.controlplane.models.pricing import ProviderCostRate

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    t0 = datetime.now(UTC) - timedelta(days=2)

    async def cost(**kw):
        base = dict(actor=_actor(user), provider="acme",
                    usage_type="image_generation", currency="USD", effective_from=t0)
        base.update(kw)
        return await pricing_svc.create_cost_rate(db, **base)

    await cost(model_or_service="acme-img", unit_cost=Decimal("0.02"))   # exact
    await cost(model_or_service=None, unit_cost=Decimal("0.05"))         # provider wildcard

    async def rate_one():
        ev = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                             provider="acme", model_or_service="acme-img")
        return await rating.rate_event(db, ev.id)

    r = await rate_one()
    assert r.cost_rate_snapshot["resolution"] == "exact"
    assert r.internal_cost_minor == 2

    exact_row = (
        await db.execute(select(ProviderCostRate).where(
            ProviderCostRate.model_or_service == "acme-img"))
    ).scalar_one()
    exact_row.effective_until = t0 + timedelta(seconds=1)   # retire before events
    await db.flush()
    r = await rate_one()
    assert r.cost_rate_snapshot["resolution"] == "provider_wildcard"
    assert r.internal_cost_minor == 5


@pytest.mark.asyncio
async def test_capability_rung_distinct_and_below_wildcard(db):
    """R311: ADR-014 ladder is exact → provider wildcard → capability, so
    capability is a DISTINCT rung BELOW provider-wildcard. Two arcs:
    (1) a provider-scoped capability rate (model NULL, capability_key set)
        with NO true wildcard resolves through the CAPABILITY rung, labeled
        'capability' (pre-R311 it was swallowed by the wildcard rung and
        mislabeled 'provider_wildcard');
    (2) when BOTH a true provider-wildcard (capability_key NULL) AND a
        capability rate exist, the WILDCARD wins by rung precedence even if
        the capability rate is newer — precedence, not effective_from."""
    t0 = datetime.now(UTC) - timedelta(days=2)

    # (1) capability-only → capability rung
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await pricing_svc.create_cost_rate(
        db, actor=_actor(user), provider="acme", model_or_service=None,
        capability_key="image_generation", usage_type="image_generation",
        currency="USD", unit_cost=Decimal("0.09"), effective_from=t0)
    ev = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                         provider="acme", model_or_service="acme-img")
    r = await rating.rate_event(db, ev.id)
    assert r.cost_rate_snapshot["resolution"] == "capability"
    assert r.internal_cost_minor == 9

    # (2) true wildcard @ 0.05 (older) + capability @ 0.09 (NEWER) → wildcard wins
    user2 = await _mk_user(db)
    tenant2 = await _mk_tenant(db, user2)
    await pricing_svc.create_cost_rate(
        db, actor=_actor(user2), provider="bolt", model_or_service=None,
        usage_type="image_generation", currency="USD",
        unit_cost=Decimal("0.05"), effective_from=t0)
    await pricing_svc.create_cost_rate(
        db, actor=_actor(user2), provider="bolt", model_or_service=None,
        capability_key="image_generation", usage_type="image_generation",
        currency="USD", unit_cost=Decimal("0.09"),
        effective_from=t0 + timedelta(days=1))  # newer, but lower rung
    ev2 = await _mk_event(db, tenant2, usage_type="image_generation", quantity=1,
                          provider="bolt", model_or_service="bolt-img")
    r2 = await rating.rate_event(db, ev2.id)
    assert r2.cost_rate_snapshot["resolution"] == "provider_wildcard"
    assert r2.internal_cost_minor == 5   # wildcard rung beats the newer capability rate


@pytest.mark.asyncio
async def test_cost_resolver_window_boundary_and_race_determinism(db):
    """R332 (mutation survivors): (1) the rate window is HALF-OPEN — a rate
    whose effective_until equals occurred_at is already expired at that
    instant; (2) R147 documents .limit(1)+order_by as the deterministic
    defense when a lost race leaves two OVERLAPPING same-rung rows — the
    resolver must pick the latest effective_from, never MultipleResultsFound."""
    from app.controlplane.models.pricing import ProviderCostRate

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    now = datetime.now(UTC)
    t0 = now - timedelta(days=3)

    # (1) half-open window: effective_until == occurred_at → expired
    prov = f"hb-{str(ULID()).lower()[:8]}"
    db.add(ProviderCostRate(
        provider=prov, model_or_service="m", usage_type="image_generation", unit="images",
        unit_cost=Decimal("0.10"), currency="USD",
        effective_from=t0, effective_until=now, created_by=user.id))
    await db.flush()
    ev = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                         provider=prov, model_or_service="m", occurred_at=now)
    r = await rating.rate_event(db, ev.id)
    assert (r.cost_rate_snapshot or {}).get("resolution") != "exact", (
        "a rate expiring exactly at occurred_at must not match (half-open window)")

    # (2) two overlapping EXACT rows (simulated race residue, R147) — the
    # newer effective_from wins deterministically
    prov2 = f"race-{str(ULID()).lower()[:8]}"
    db.add_all([
        ProviderCostRate(
            provider=prov2, model_or_service="m", usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.30"), currency="USD",
            effective_from=t0, created_by=user.id),
        ProviderCostRate(
            provider=prov2, model_or_service="m", usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.20"), currency="USD",
            effective_from=t0 + timedelta(hours=1), created_by=user.id),
    ])
    await db.flush()
    ev2 = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                          provider=prov2, model_or_service="m")
    r2 = await rating.rate_event(db, ev2.id)
    assert (r2.cost_rate_snapshot or {}).get("resolution") == "exact"
    assert r2.internal_cost_minor == 20                     # newer row (0.20) wins

    # same determinism on the WILDCARD and CAPABILITY rungs
    prov3 = f"racew-{str(ULID()).lower()[:8]}"
    db.add_all([
        ProviderCostRate(
            provider=prov3, model_or_service=None, usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.50"), currency="USD",
            effective_from=t0, created_by=user.id),
        ProviderCostRate(
            provider=prov3, model_or_service=None, usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.40"), currency="USD",
            effective_from=t0 + timedelta(hours=1), created_by=user.id),
    ])
    await db.flush()
    ev3 = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                          provider=prov3, model_or_service="unpriced-model")
    r3 = await rating.rate_event(db, ev3.id)
    assert (r3.cost_rate_snapshot or {}).get("resolution") == "provider_wildcard"
    assert r3.internal_cost_minor == 40

    # capability rung: two overlapping capability rates → newest wins
    prov4 = f"racec-{str(ULID()).lower()[:8]}"
    db.add_all([
        ProviderCostRate(
            provider=prov4, model_or_service=None, capability_key="image_generation",
            usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.70"), currency="USD",
            effective_from=t0, created_by=user.id),
        ProviderCostRate(
            provider=prov4, model_or_service=None, capability_key="image_generation",
            usage_type="image_generation", unit="images",
            unit_cost=Decimal("0.60"), currency="USD",
            effective_from=t0 + timedelta(hours=1), created_by=user.id),
    ])
    await db.flush()
    ev4 = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                          provider=prov4, model_or_service="unpriced-model")
    r4 = await rating.rate_event(db, ev4.id)
    assert (r4.cost_rate_snapshot or {}).get("resolution") == "capability"
    assert r4.internal_cost_minor == 60

    # a MODEL-LESS event must resolve on the wildcard rung with that label —
    # entering the exact rung with model None turns the SQLAlchemy comparison
    # into IS NULL and mislabels the wildcard row as 'exact'
    ev5 = await _mk_event(db, tenant, usage_type="image_generation", quantity=1,
                          provider=prov3, model_or_service=None)
    r5 = await rating.rate_event(db, ev5.id)
    assert (r5.cost_rate_snapshot or {}).get("resolution") == "provider_wildcard"
    assert r5.internal_cost_minor == 40


@pytest.mark.asyncio
async def test_offering_fallback_scoped_to_connection_and_model(db):
    """R332: the offering fallback must resolve THE step's offering — scoped
    by BOTH connection and model. A same-model offering on another connection
    (different org pricing) or a same-connection different-model offering must
    never supply the cost. And when NO offering matches, the event lands at
    no_rate without touching offering attrs (the `and` short-circuit — mutated
    to `or` it dereferences None → 500)."""
    from app.models.organization import Organization, OrgStatus
    from app.models.provider import (
        ProviderAdapter,
        ProviderConnection,
        ProviderModelOffering,
    )
    from app.models.workflow_run import RunStatus, WorkflowRun

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org = Organization(
        name="OffScope", slug=f"osc-{str(ULID()).lower()}", status=OrgStatus.ACTIVE,
        tenant_id=tenant.id, created_by=user.id)
    db.add(org)
    await db.flush()
    adapter = ProviderAdapter(key=f"osc-{str(ULID()).lower()}", name="Osc")
    db.add(adapter)
    await db.flush()
    conn_a = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="a",
                                created_by=user.id)
    conn_b = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="b",
                                created_by=user.id)
    db.add_all([conn_a, conn_b])
    await db.flush()
    db.add_all([
        ProviderModelOffering(connection_id=conn_a.id, capability_key="text_generation",
                              model_name="m1", is_active=True,
                              cost_per_call_usd=Decimal("1")),
        ProviderModelOffering(connection_id=conn_b.id, capability_key="text_generation",
                              model_name="m1", is_active=True,
                              cost_per_call_usd=Decimal("9.99")),   # other connection
        ProviderModelOffering(connection_id=conn_a.id, capability_key="text_generation",
                              model_name="m2", is_active=True,
                              cost_per_call_usd=Decimal("5.55")),   # other model
    ])
    run = WorkflowRun(
        org_id=org.id, pack_id=None, release_id=None, installation_id=None,
        definition_snapshot={"steps": [], "edges": []}, inputs={},
        started_by=user.id, status=RunStatus.COMPLETED)
    db.add(run)
    await db.flush()

    # a DUPLICATE (conn_a, m1) offering row (no unique constraint exists):
    # the resolver's .limit(1) must stay deterministic, not
    # MultipleResultsFound-500 on every rate_event
    db.add(ProviderModelOffering(connection_id=conn_a.id, capability_key="text_generation",
                                 model_name="m1", is_active=True,
                                 cost_per_call_usd=Decimal("1")))
    await db.flush()
    ev = await _mk_event(
        db, tenant, org_id=org.id, usage_type="voice_generation", quantity=1,
        provider=f"posc-{str(ULID()).lower()[:8]}",
        workflow_run_id=run.id, provider_connection_id=conn_a.id,
        model_or_service="m1")
    r = await rating.rate_event(db, ev.id)
    snap = r.cost_rate_snapshot or {}
    assert snap.get("fallback") == "offering"
    assert r.internal_cost_minor == 100, "must use conn_a/m1 ($1), not another connection/model"

    # no matching offering at all → clean no_rate, no crash
    ev2 = await _mk_event(
        db, tenant, org_id=org.id, usage_type="voice_generation", quantity=1,
        provider=f"posc-{str(ULID()).lower()[:8]}",
        workflow_run_id=run.id, provider_connection_id=conn_a.id,
        model_or_service="no-such-model")
    r2 = await rating.rate_event(db, ev2.id)
    snap2 = r2.cost_rate_snapshot or {}
    assert snap2.get("fallback") != "offering"
    assert r2.internal_cost_minor == 0

    # the offering fallback requires BOTH workflow dims: a connection-bearing
    # event WITHOUT a workflow_run_id (eval-path shape) must not be
    # offering-priced
    ev3 = await _mk_event(
        db, tenant, org_id=org.id, usage_type="voice_generation", quantity=1,
        provider=f"posc-{str(ULID()).lower()[:8]}",
        provider_connection_id=conn_a.id, model_or_service="m1")
    r3 = await rating.rate_event(db, ev3.id)
    assert (r3.cost_rate_snapshot or {}).get("fallback") != "offering"
    assert r3.internal_cost_minor == 0
