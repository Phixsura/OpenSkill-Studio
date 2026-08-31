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
    ]:
        with pytest.raises(AppError):
            v(policy_type, params)


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
        async with AsyncSessionLocal() as db:
            await process_outbox_once(db, topics=["usage.recorded"])
        async with AsyncSessionLocal() as db:
            rated = (
                await db.execute(select(RatedUsage).where(RatedUsage.usage_event_id == event_id))
            ).scalar_one_or_none()
            assert rated is not None
            assert rated.status == "rated"
    finally:
        await engine.dispose()
