"""P5 DB tests: credit ledger, reservations, budgets, eval-budget migration."""

import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.credit import (
    BudgetPolicy,
    CreditLedgerEntry,
    CreditReservation,
    TenantCreditBalance,
)
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import budgets as budget_svc
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
        email=f"cp5-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="CP5",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"C {ULID()}",
        slug=f"c-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


def _actor(user):
    return Actor(user_id=user.id, type="platform")


# ── Ledger round trips ───────────────────────────────────────


@pytest.mark.asyncio
async def test_ledger_entry_types_and_balance_after(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 10000, actor=a)
    await credit_svc.grant_promotional(
        db,
        tenant.id,
        "USD",
        2000,
        expires_at=datetime.now(UTC) + timedelta(days=30),
        reason="welcome",
        actor=a,
    )
    await credit_svc.debit(
        db, tenant.id, "USD", 3000, reference_type="manual", reference_id=str(ULID())
    )
    await credit_svc.refund(
        db,
        tenant.id,
        "USD",
        500,
        reference_type="purchase",
        reference_id=str(ULID()),
        reason="partial refund",
        actor=a,
    )
    await credit_svc.adjust(db, tenant.id, "USD", -100, reason="rounding fix", actor=a)
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(
                TenantCreditBalance.tenant_id == tenant.id,
                TenantCreditBalance.currency == "USD",
            )
        )
    ).scalar_one()
    assert balance.balance_minor == 10000 + 2000 - 3000 + 500 - 100
    # Ledger replay: last balance_after == materialized balance
    entries = (
        (
            await db.execute(
                select(CreditLedgerEntry)
                .where(CreditLedgerEntry.tenant_id == tenant.id)
                .order_by(CreditLedgerEntry.created_at, CreditLedgerEntry.id)
            )
        )
        .scalars()
        .all()
    )
    assert entries[-1].balance_after_minor == balance.balance_minor
    running = 0
    for e in entries:
        running += e.amount_minor
        assert e.balance_after_minor == running


@pytest.mark.asyncio
async def test_insufficient_credit_and_idempotency(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 100, actor=a)
    with pytest.raises(AppError) as exc:
        await credit_svc.debit(
            db, tenant.id, "USD", 200, reference_type="manual", reference_id=str(ULID())
        )
    assert exc.value.code == "INSUFFICIENT_CREDIT"
    # Idempotent top-up
    key = f"topup-{ULID()}"
    first = await credit_svc.top_up(db, tenant.id, "USD", 50, actor=a, idempotency_key=key)
    second = await credit_svc.top_up(db, tenant.id, "USD", 50, actor=a, idempotency_key=key)
    assert first is not None and second is None
    balance = (
        await db.execute(
            select(TenantCreditBalance.balance_minor).where(
                TenantCreditBalance.tenant_id == tenant.id
            )
        )
    ).scalar_one()
    assert balance == 150


# ── Concurrency (issue §39 acceptance) ───────────────────────


@pytest.mark.asyncio
async def test_concurrent_debits_never_negative():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            await credit_svc.top_up(setup, tenant.id, "USD", 1000, actor=_actor(user))
            await setup.commit()
            tid = tenant.id

        async def spend():
            async with AsyncSessionLocal() as s:
                try:
                    await credit_svc.debit(
                        s, tid, "USD", 100, reference_type="manual", reference_id=str(ULID())
                    )
                    await s.commit()
                    return True
                except AppError:
                    await s.rollback()
                    return False

        results = await asyncio.gather(*[spend() for _ in range(20)])
        assert sum(results) == 10  # exactly 1000/100 succeed
        async with AsyncSessionLocal() as s:
            balance = (
                await s.execute(
                    select(TenantCreditBalance.balance_minor).where(
                        TenantCreditBalance.tenant_id == tid
                    )
                )
            ).scalar_one()
            assert balance == 0  # never negative
    finally:
        await engine.dispose()


# ── Reservations ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_reserve_settle_release_paths(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 1000, actor=a)
    ref = str(ULID())
    r = await credit_svc.reserve(
        db, tenant.id, "USD", 300, reference_type="workflow_run", reference_id=ref
    )
    # Duplicate reserve is idempotent
    r2 = await credit_svc.reserve(
        db, tenant.id, "USD", 300, reference_type="workflow_run", reference_id=ref
    )
    assert r2.id == r.id
    # Available shrinks: 1000-300=700 → an 800 debit fails
    with pytest.raises(AppError):
        await credit_svc.debit(
            db, tenant.id, "USD", 800, reference_type="manual", reference_id=str(ULID())
        )
    # Settle for LESS than the hold (failed steps → actual only, issue §16)
    settled = await credit_svc.settle(db, r.id, 120)
    assert settled.status == "settled" and settled.settled_amount_minor == 120
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.balance_minor == 880 and balance.reserved_minor == 0
    # Settle again = idempotent no-op
    again = await credit_svc.settle(db, r.id, 999)
    assert again.settled_amount_minor == 120
    # Release path
    r3 = await credit_svc.reserve(
        db, tenant.id, "USD", 200, reference_type="workflow_run", reference_id=str(ULID())
    )
    released = await credit_svc.release(db, r3.id)
    assert released.status == "released"
    await db.refresh(balance)
    assert balance.reserved_minor == 0 and balance.balance_minor == 880


@pytest.mark.asyncio
async def test_settle_over_hold_floors_at_balance(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await credit_svc.top_up(db, tenant.id, "USD", 100, actor=_actor(user))
    r = await credit_svc.reserve(
        db, tenant.id, "USD", 50, reference_type="workflow_run", reference_id=str(ULID())
    )
    await credit_svc.settle(db, r.id, 500)  # actual >> balance
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.balance_minor == 0  # floored, never negative
    entry = (
        await db.execute(
            select(CreditLedgerEntry).where(CreditLedgerEntry.idempotency_key == f"settle:{r.id}")
        )
    ).scalar_one()
    assert "shortfall" in (entry.reason or "")


@pytest.mark.asyncio
async def test_concurrent_settle_vs_release_single_winner():
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            await credit_svc.top_up(setup, tenant.id, "USD", 1000, actor=_actor(user))
            r = await credit_svc.reserve(
                setup,
                tenant.id,
                "USD",
                400,
                reference_type="workflow_run",
                reference_id=str(ULID()),
            )
            await setup.commit()
            rid = r.id

        async def do_settle():
            async with AsyncSessionLocal() as s:
                res = await credit_svc.settle(s, rid, 400)
                await s.commit()
                return res.status

        async def do_release():
            async with AsyncSessionLocal() as s:
                res = await credit_svc.release(s, rid)
                await s.commit()
                return res.status

        s1, s2 = await asyncio.gather(do_settle(), do_release())
        # Both return the same terminal status — exactly one transition won
        assert s1 == s2
        async with AsyncSessionLocal() as s:
            r = await s.get(CreditReservation, rid)
            balance = (
                await s.execute(
                    select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == r.tenant_id)
                )
            ).scalar_one()
            assert balance.reserved_minor == 0
            if r.status == "settled":
                assert balance.balance_minor == 600
            else:
                assert balance.balance_minor == 1000
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_promo_expiry(db):
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await credit_svc.grant_promotional(
        db,
        tenant.id,
        "USD",
        500,
        expires_at=datetime.now(UTC) - timedelta(days=1),  # already expired
        reason="expired promo",
        actor=_actor(user),
    )
    n = await credit_svc.expire_promotional(db)
    assert n >= 1
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.balance_minor == 0
    # Rerun: no-op (lot marked consumed)
    await credit_svc.expire_promotional(db)
    entries = (
        (
            await db.execute(
                select(CreditLedgerEntry).where(
                    CreditLedgerEntry.tenant_id == tenant.id,
                    CreditLedgerEntry.entry_type == "expiration",
                )
            )
        )
        .scalars()
        .all()
    )
    assert len(entries) == 1


@pytest.mark.asyncio
async def test_expire_stale_reservations(db):
    """R22: the reservation-expiry sweep releases an expired non-running hold
    (freeing reserved credit) and leaves a still-valid hold untouched."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = _actor(user)
    await credit_svc.top_up(db, tenant.id, "USD", 1000, actor=a)
    stale = await credit_svc.reserve(
        db, tenant.id, "USD", 300, reference_type="manual", reference_id="stale-ref"
    )
    stale.expires_at = datetime.now(UTC) - timedelta(hours=1)
    fresh = await credit_svc.reserve(
        db, tenant.id, "USD", 200, reference_type="manual", reference_id="fresh-ref"
    )
    await db.flush()
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    assert balance.reserved_minor == 500

    handled = await credit_svc.expire_stale_reservations(db)
    await db.flush()
    assert handled >= 1
    await db.refresh(stale)
    await db.refresh(fresh)
    await db.refresh(balance)
    assert stale.status == "released"
    assert fresh.status == "held"
    assert balance.reserved_minor == 200  # only the stale hold freed


# ── Budgets ──────────────────────────────────────────────────


def test_budget_policy_matching_matrix():
    def mk(scope_type, scope_id=None, capability=None, usage_type=None):
        return BudgetPolicy(
            tenant_id="t",
            scope_type=scope_type,
            scope_id=scope_id,
            period="monthly",
            capability_key=capability,
            usage_type=usage_type,
            limit_minor=100,
            currency="USD",
        )

    m = budget_svc.policy_matches
    ctx = dict(
        org_id="o1",
        project_id="p1",
        cohort_id=None,
        user_id="u1",
        capability="image_generation",
        usage_type="image_generation",
    )
    assert m(mk("tenant"), **ctx)
    assert m(mk("org", "o1"), **ctx)
    assert not m(mk("org", "o2"), **ctx)
    assert m(mk("project", "p1"), **ctx)
    assert not m(mk("cohort", "c1"), **ctx)  # no cohort in context
    assert m(mk("user", "u1"), **ctx)
    assert m(mk("tenant", capability="image_generation"), **ctx)
    assert not m(mk("tenant", capability="video_generation"), **ctx)
    assert not m(mk("tenant", usage_type="llm_input_tokens"), **ctx)


@pytest.mark.asyncio
async def test_budget_hard_stop_and_ceiling(db):
    from app.controlplane.services import metering, rating

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # Org-scope monthly budget of 1.00 USD (100 minor)
    db.add(
        BudgetPolicy(
            tenant_id=tenant.id,
            scope_type="org",
            scope_id="01JFAKEORGFAKEORGFAKEORGFA",
            period="monthly",
            limit_minor=100,
            currency="USD",
            hard_stop=True,
        )
    )
    await db.flush()
    # Under budget passes
    decision = await budget_svc.check(db, tenant, "01JFAKEORGFAKEORGFAKEORGFA", projected_minor=50)
    assert decision.allowed
    # Generate billable spend beyond the limit: tenant-specific fixed price
    from app.controlplane.services import pricing as pricing_svc

    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"b {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 100},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JFAKEORGFAKEORGFAKEORGFA",
        usage_type="image_generation",
        quantity=2,  # 2×100 = 200 minor > 100 limit
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=f"bud-{ULID()}",
    )
    await rating.rate_event(db, event.id)
    with pytest.raises(AppError) as exc:
        await budget_svc.check(db, tenant, "01JFAKEORGFAKEORGFAKEORGFA")
    assert exc.value.code == "BUDGET_EXCEEDED"
    # Soft policy: warns instead
    policy = (
        await db.execute(select(BudgetPolicy).where(BudgetPolicy.tenant_id == tenant.id))
    ).scalar_one()
    policy.hard_stop = False
    await db.flush()
    decision = await budget_svc.check(db, tenant, "01JFAKEORGFAKEORGFAKEORGFA")
    assert decision.allowed and decision.warnings


@pytest.mark.asyncio
async def test_tenant_ai_ceiling_enforced_without_policy_row(db):
    """R15: max_ai_budget_usd_month entitlement acts as an implicit
    tenant-scope monthly hard ceiling — enforced with NO BudgetPolicy row."""
    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.controlplane.services import metering, rating
    from app.controlplane.services import pricing as pricing_svc
    from app.controlplane.services.entitlements import invalidate_cache

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # $0.50 ceiling = 50 minor
    db.add(
        TenantEntitlementOverride(
            tenant_id=tenant.id,
            key="max_ai_budget_usd_month",
            value={"v": "0.5"},
            reason="probe ceiling",
            enforcement="hard",
        )
    )
    await db.flush()
    await invalidate_cache(tenant.id)
    await pricing_svc.create_price_policy(
        db,
        actor=_actor(user),
        name=f"ceil {ULID()}",
        policy_type="fixed_unit_price",
        usage_type="image_generation",
        currency="USD",
        params={"unit_price_minor": 100},
        effective_from=datetime.now(UTC) - timedelta(days=1),
        tenant_id=tenant.id,
    )
    event = await metering.emit_usage(
        db,
        tenant_id=tenant.id,
        org_id="01JCEILORGCEILORGCEILORGCE",
        usage_type="image_generation",
        quantity=1,  # 100 minor > 50 ceiling
        occurred_at=datetime.now(UTC),
        source="manual",
        idempotency_key=f"ceil-{ULID()}",
    )
    await rating.rate_event(db, event.id)
    # No BudgetPolicy row exists for this org, yet the ceiling blocks
    with pytest.raises(AppError) as exc:
        await budget_svc.check(db, tenant, "01JCEILORGCEILORGCEILORGCE")
    assert exc.value.code == "BUDGET_EXCEEDED"


@pytest.mark.asyncio
async def test_eval_settings_write_through(db):
    """Issue §17: PUT settings/evaluation creates/updates/removes the policy."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org_id = f"01J{str(ULID())[3:]}"
    await budget_svc.upsert_from_eval_settings(db, tenant.id, org_id, 250.0)
    policy = (
        await db.execute(
            select(BudgetPolicy).where(
                BudgetPolicy.tenant_id == tenant.id, BudgetPolicy.scope_id == org_id
            )
        )
    ).scalar_one()
    assert policy.limit_minor == 25000
    assert policy.metadata_["source"] == "eval_settings"
    await budget_svc.upsert_from_eval_settings(db, tenant.id, org_id, 300.0)
    await db.refresh(policy)
    assert policy.limit_minor == 30000
    await budget_svc.upsert_from_eval_settings(db, tenant.id, org_id, None)
    gone = (
        await db.execute(
            select(BudgetPolicy).where(
                BudgetPolicy.tenant_id == tenant.id, BudgetPolicy.scope_id == org_id
            )
        )
    ).scalar_one_or_none()
    assert gone is None


# ── run.terminal settlement handler ──────────────────────────


@pytest.mark.asyncio
async def test_run_terminal_settles_actual_usage():
    from app.controlplane.models.outbox import enqueue
    from app.controlplane.services import metering
    from app.controlplane.services import pricing as pricing_svc
    from app.controlplane.worker import process_outbox_once
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as db:
            user = await _mk_user(db)
            tenant = await _mk_tenant(db, user)
            a = _actor(user)
            await credit_svc.top_up(db, tenant.id, "USD", 10000, actor=a)
            run_id = str(ULID())
            await credit_svc.reserve(
                db,
                tenant.id,
                "USD",
                1000,
                reference_type="workflow_run",
                reference_id=run_id,
            )
            # Tenant-priced usage from the "run": 3 images × 50 = 150 minor
            await pricing_svc.create_price_policy(
                db,
                actor=a,
                name=f"rt {ULID()}",
                policy_type="fixed_unit_price",
                usage_type="image_generation",
                currency="USD",
                params={"unit_price_minor": 50},
                effective_from=datetime.now(UTC) - timedelta(days=1),
                tenant_id=tenant.id,
            )
            await metering.emit_usage(
                db,
                tenant_id=tenant.id,
                org_id="01JFAKEORGFAKEORGFAKEORGFA",
                usage_type="image_generation",
                quantity=3,
                occurred_at=datetime.now(UTC),
                source="workflow_runtime",
                idempotency_key=f"rt-{ULID()}",
                workflow_run_id=run_id,
            )
            enqueue(db, "run.terminal", {"run_id": run_id, "status": "completed"})
            await db.commit()
            tid = tenant.id

        # Drain until quiet, SCOPED to this test's topics — a full-suite run
        # leaves unrelated backlog that would otherwise exhaust the pass
        # budget before reaching our messages. usage.recorded rates the
        # events; run.terminal then settles the reservation with actual usage.
        for _ in range(30):
            async with AsyncSessionLocal() as db:
                if await process_outbox_once(db, topics=["usage.recorded", "run.terminal"]) == 0:
                    break

        async with AsyncSessionLocal() as db:
            balance = (
                await db.execute(
                    select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tid)
                )
            ).scalar_one()
            assert balance.reserved_minor == 0
            assert balance.balance_minor == 10000 - 150  # actual, not the 1000 hold
        # R38/C11: the settled rows are marked 'settled' so a period invoice
        # does NOT re-bill usage already paid by the reservation (no double
        # charge).
        async with AsyncSessionLocal() as db:
            from app.controlplane.models.pricing import RatedUsage
            from app.controlplane.models.usage import UsageEvent

            rows = (
                (
                    await db.execute(
                        select(RatedUsage)
                        .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
                        .where(UsageEvent.workflow_run_id == run_id)
                    )
                )
                .scalars()
                .all()
            )
            assert rows and all(r.status == "settled" for r in rows)
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_credit_settled_usage_not_reinvoiced():
    """R38/C11+C35: usage paid via a credit reservation (settle at
    run.terminal) must NOT appear on the period invoice — the reservation IS
    the payment. The rows are 'settled', which close_period_and_invoice's
    'rated'-only usage-line query skips → no double charge."""
    from app.controlplane.models.billing import BillingPeriod, InvoiceLine
    from app.controlplane.models.outbox import enqueue
    from app.controlplane.services import billing as billing_svc
    from app.controlplane.services import metering
    from app.controlplane.services import pricing as pricing_svc
    from app.controlplane.worker import process_outbox_once
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as db:
            user = await _mk_user(db)
            tenant = await _mk_tenant(db, user)
            a = _actor(user)
            await credit_svc.top_up(db, tenant.id, "USD", 100000, actor=a)
            sub, _ = await billing_svc.start_subscription(
                db, tenant, plan_key="school", interval="month", seats=0,
                provider="manual", actor=a,
            )
            await pricing_svc.create_price_policy(
                db, actor=a, name=f"cs {ULID()}", policy_type="fixed_unit_price",
                usage_type="image_generation", currency="USD",
                params={"unit_price_minor": 50},
                effective_from=datetime.now(UTC) - timedelta(days=1), tenant_id=tenant.id,
            )
            run_id = str(ULID())
            await credit_svc.reserve(
                db, tenant.id, "USD", 1000, reference_type="workflow_run", reference_id=run_id
            )
            await metering.emit_usage(
                db, tenant_id=tenant.id, org_id="01JFAKEORGFAKEORGFAKEORGFA",
                usage_type="image_generation", quantity=3,
                occurred_at=datetime.now(UTC) - timedelta(minutes=5),
                source="workflow_runtime", idempotency_key=f"cs-{ULID()}",
                workflow_run_id=run_id,
            )
            enqueue(db, "run.terminal", {"run_id": run_id, "status": "completed"})
            await db.commit()
            tid, sub_id = tenant.id, sub.id
        # settle via the handler (scoped drain)
        for _ in range(30):
            async with AsyncSessionLocal() as db:
                if (
                    await process_outbox_once(db, topics=["usage.recorded", "run.terminal"])
                    == 0
                ):
                    break
        # force the period closed → invoice
        async with AsyncSessionLocal() as db:
            period = (
                await db.execute(
                    select(BillingPeriod).where(BillingPeriod.subscription_id == sub_id)
                )
            ).scalar_one()
            period.period_end = datetime.now(UTC) - timedelta(seconds=1)
            await db.flush()
            invoice = await billing_svc.close_period_and_invoice(db, period.id)
            await db.commit()
            inv_id = invoice.id
        async with AsyncSessionLocal() as db:
            lines = (
                (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == inv_id)))
                .scalars()
                .all()
            )
            usage_lines = [ln for ln in lines if ln.line_type == "usage"]
            # The credit-settled usage must NOT be re-billed as a usage line.
            assert not usage_lines, [ln.amount_minor for ln in usage_lines]
            # Credit balance = start − settle(150) − plan-line credit(19900).
            # The 150 is charged exactly ONCE (the settle); the invoice draws
            # credit only for its legitimate plan line, not the settled usage.
            plan_line = next(ln for ln in lines if ln.line_type == "plan")
            balance = (
                await db.execute(
                    select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tid)
                )
            ).scalar_one()
            assert balance.balance_minor == 100000 - 150 - plan_line.amount_minor
    finally:
        await engine.dispose()
