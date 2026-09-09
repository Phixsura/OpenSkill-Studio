"""R153 — property/invariant fuzz over the credit ledger and the billing
void/re-close machine. Code-reading rounds (R136-R152) converged; these tests
attack the same machinery with randomized OPERATION SEQUENCES and check the
system-level invariants every reading assumed:

  I1  balance_minor == Σ(ledger amounts) per (tenant, currency)
  I2  every returned entry's balance_after equals the running sum at that op
  I3  reserved_minor == Σ(amount of reservations still 'held'); 0 ≤ reserved ≤ balance
  I4  the same invariants hold under CONCURRENT writers
  I5  void + re-close with no forward changes reproduces the invoice
      line-for-line (the close_snapshot machine's core promise)

Seeds are fixed per test for reproducibility; bump SEEDS to widen the search.
"""

import asyncio
import random
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from ulid import ULID

from app.controlplane.models.credit import CreditLedgerEntry, CreditReservation, TenantCreditBalance
from app.controlplane.models.tenant import TenantAccount, TenantStatus
from app.controlplane.services import credits as credit_svc
from app.controlplane.services import tenants as tenant_svc
from app.controlplane.services.audit import Actor
from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.exceptions import AppError
from app.models.user import User, UserRole, UserStatus

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def db():
    from app.core.database import engine

    await engine.dispose(close=False)
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()
    await engine.dispose()


async def _mk_user(db) -> User:
    user = User(
        email=f"prop-{ULID()}@test.com",
        email_verified=True,
        password_hash=hash_password("Test1234!"),
        display_name="Prop",
        role=UserRole.STUDENT,
        status=UserStatus.ACTIVE,
    )
    db.add(user)
    await db.flush()
    return user


async def _mk_tenant(db, user) -> TenantAccount:
    return await tenant_svc.create_tenant(
        db,
        name=f"P {ULID()}",
        slug=f"p-{str(ULID()).lower()}",
        actor=Actor(user_id=user.id, type="platform"),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
    )


async def _assert_ledger_invariants(s, tenant_id: str) -> None:
    balances = (
        (
            await s.execute(
                select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant_id)
            )
        )
        .scalars()
        .all()
    )
    for bal in balances:
        entries = (
            (
                await s.execute(
                    select(CreditLedgerEntry).where(
                        CreditLedgerEntry.tenant_id == tenant_id,
                        CreditLedgerEntry.currency == bal.currency,
                    )
                )
            )
            .scalars()
            .all()
        )
        total = sum(e.amount_minor for e in entries)
        assert bal.balance_minor == total, (
            f"I1 violated [{bal.currency}]: balance {bal.balance_minor} != Σamounts {total}"
        )
        held = (
            (
                await s.execute(
                    select(CreditReservation).where(
                        CreditReservation.tenant_id == tenant_id,
                        CreditReservation.currency == bal.currency,
                        CreditReservation.status == "held",
                    )
                )
            )
            .scalars()
            .all()
        )
        held_sum = sum(r.amount_minor for r in held)
        assert bal.reserved_minor == held_sum, (
            f"I3 violated [{bal.currency}]: reserved {bal.reserved_minor} != Σheld {held_sum}"
        )
        assert 0 <= bal.reserved_minor <= bal.balance_minor, (
            f"I3 bounds violated [{bal.currency}]: 0 ≤ {bal.reserved_minor} ≤ {bal.balance_minor}"
        )


SEEDS = (1, 7, 42)


@pytest.mark.parametrize("seed", SEEDS)
async def test_credit_ledger_invariants_sequential_fuzz(db, seed):
    """~150 random ops through the public credit API; I1/I2/I3 after every
    expiry pass and at the end."""
    rng = random.Random(seed)
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = Actor(user_id=user.id, type="platform")
    running = 0  # I2: expected balance in USD minor
    holds: list = []

    for i in range(150):
        op = rng.choice(
            ["top_up", "adjust+", "adjust-", "reserve", "settle", "release", "refund", "promo", "expire"]
        )
        try:
            if op == "top_up":
                amt = rng.randint(1, 5000)
                e = await credit_svc.top_up(
                    db, tenant.id, "USD", amt, actor=a, idempotency_key=f"f{seed}-{i}"
                )
                if e is not None:
                    running += amt
                    assert e.balance_after_minor == running, f"I2 @op{i} top_up"
            elif op == "adjust+":
                amt = rng.randint(1, 3000)
                e = await credit_svc.adjust(db, tenant.id, "USD", amt, reason="f", actor=a)
                running += amt
                assert e.balance_after_minor == running, f"I2 @op{i} adjust+"
            elif op == "adjust-":
                amt = rng.randint(1, 3000)
                try:
                    e = await credit_svc.adjust(db, tenant.id, "USD", -amt, reason="f", actor=a)
                    running -= amt
                    assert e.balance_after_minor == running, f"I2 @op{i} adjust-"
                except AppError as ex:
                    assert ex.code == "INSUFFICIENT_CREDIT"
            elif op == "reserve":
                amt = rng.randint(1, 2000)
                try:
                    h = await credit_svc.reserve(
                        db, tenant.id, "USD", amt,
                        reference_type="workflow_run", reference_id=str(ULID()),
                    )
                    holds.append(h)
                except AppError as ex:
                    assert ex.code in ("INSUFFICIENT_CREDIT",)
            elif op == "settle" and holds:
                h = holds.pop(rng.randrange(len(holds)))
                actual = rng.randint(0, int(h.amount_minor * 1.5))
                before = running
                r = await credit_svc.settle(db, h.id, actual)
                if r.status == "settled":
                    # charged = min(actual, available-after-own-hold-release)
                    bal = (
                        await db.execute(
                            select(TenantCreditBalance).where(
                                TenantCreditBalance.tenant_id == tenant.id,
                                TenantCreditBalance.currency == "USD",
                            )
                        )
                    ).scalar_one()
                    running = bal.balance_minor  # derive; validated by I1 at end
                    assert before - running <= actual, f"settle overcharged @op{i}"
            elif op == "release" and holds:
                h = holds.pop(rng.randrange(len(holds)))
                await credit_svc.release(db, h.id)
            elif op == "refund":
                amt = rng.randint(1, 1500)
                e = await credit_svc.refund(
                    db, tenant.id, "USD", amt,
                    reference_type="purchase", reference_id=str(ULID()),
                    reason="f", actor=a, idempotency_key=f"r{seed}-{i}",
                )
                if e is not None:
                    running += amt
                    assert e.balance_after_minor == running, f"I2 @op{i} refund"
            elif op == "promo":
                amt = rng.randint(1, 2000)
                expires = datetime.now(UTC) + timedelta(days=rng.choice([-1, 30]))
                e = await credit_svc.grant_promotional(
                    db, tenant.id, "USD", amt, expires_at=expires, reason="f", actor=a,
                    idempotency_key=f"p{seed}-{i}",
                )
                if e is not None:
                    running += amt
                    assert e.balance_after_minor == running, f"I2 @op{i} promo"
            elif op == "expire":
                await credit_svc.expire_promotional(db)
                bal = (
                    await db.execute(
                        select(TenantCreditBalance).where(
                            TenantCreditBalance.tenant_id == tenant.id,
                            TenantCreditBalance.currency == "USD",
                        )
                    )
                ).scalar_one_or_none()
                running = bal.balance_minor if bal else 0
                await _assert_ledger_invariants(db, tenant.id)
        except AssertionError:
            raise
    await _assert_ledger_invariants(db, tenant.id)


@pytest.mark.parametrize("seed", SEEDS)
async def test_credit_ledger_invariants_concurrent_fuzz(seed):
    """3 concurrent writers × 40 committed random ops each on ONE (tenant,
    currency); I1/I3 must hold at the end — the balance FOR UPDATE is THE
    serialization point and any lost update breaks Σ(amounts)."""
    from app.core.database import engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            # seed capital so debits mostly succeed
            await credit_svc.top_up(
                setup, tenant.id, "USD", 500_000, actor=Actor(user_id=user.id, type="platform"),
                idempotency_key=f"seedcap-{seed}",
            )
            await setup.commit()
            tenant_id, user_id = tenant.id, user.id

        async def writer(widx: int):
            wrng = random.Random(seed * 100 + widx)
            async with AsyncSessionLocal() as s:
                u = await s.get(User, user_id)
                a = Actor(user_id=u.id, type="platform")
                my_holds = []
                for j in range(40):
                    op = wrng.choice(["top_up", "adjust-", "reserve", "settle", "release", "refund"])
                    try:
                        if op == "top_up":
                            await credit_svc.top_up(
                                s, tenant_id, "USD", wrng.randint(1, 2000), actor=a,
                                idempotency_key=f"c{seed}-{widx}-{j}",
                            )
                        elif op == "adjust-":
                            await credit_svc.adjust(
                                s, tenant_id, "USD", -wrng.randint(1, 1500), reason="c", actor=a
                            )
                        elif op == "reserve":
                            my_holds.append(
                                await credit_svc.reserve(
                                    s, tenant_id, "USD", wrng.randint(1, 1000),
                                    reference_type="workflow_run", reference_id=str(ULID()),
                                )
                            )
                        elif op == "settle" and my_holds:
                            h = my_holds.pop()
                            await credit_svc.settle(s, h.id, wrng.randint(0, h.amount_minor))
                        elif op == "release" and my_holds:
                            h = my_holds.pop()
                            await credit_svc.release(s, h.id)
                        elif op == "refund":
                            await credit_svc.refund(
                                s, tenant_id, "USD", wrng.randint(1, 800),
                                reference_type="purchase", reference_id=str(ULID()),
                                reason="c", actor=a, idempotency_key=f"cr{seed}-{widx}-{j}",
                            )
                        await s.commit()
                    except AppError:
                        await s.rollback()
                    except Exception:
                        await s.rollback()
                        raise
                # leave no dangling holds: release the rest
                for h in my_holds:
                    try:
                        await credit_svc.release(s, h.id)
                        await s.commit()
                    except Exception:
                        await s.rollback()

        await asyncio.gather(writer(0), writer(1), writer(2))
        async with AsyncSessionLocal() as s:
            await _assert_ledger_invariants(s, tenant_id)
    finally:
        await engine.dispose()


@pytest.mark.parametrize("seed", (3, 11, 29, 63, 101))
async def test_void_reclose_reproduces_invoice_fuzz(db, seed):
    """I5: with NO forward changes between void and re-close, the re-closed
    invoice must reproduce the original LINE FOR LINE — randomized over
    0-3 mid-period immediate plan/seat changes plus an optional deferred
    change (the exact state space the R133→R135 snapshot rework covers)."""
    from datetime import timedelta as _td

    from app.controlplane.models.billing import (
        BillingPeriod,
        InvoiceLine,
        SubscriptionChange,
    )
    from app.controlplane.services import billing as billing_svc
    from app.controlplane.services.billing import _add_interval

    rng = random.Random(seed)
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = Actor(user_id=user.id, type="platform")
    start_seats = rng.choice([0, 150, 250, 400])
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=start_seats,
        provider="manual", actor=a,
    )
    # 0-3 mid-period immediate changes (plan flip and/or seat moves)
    n_changes = rng.randint(0, 3)
    for _ in range(n_changes):
        if rng.random() < 0.4:
            target = "growth" if sub.plan_version_id and rng.random() < 0.5 else "school"
            await billing_svc.change_plan(
                db, tenant, sub, plan_key=target, seats=None,
                proration_mode="immediate", actor=a,
            )
        else:
            await billing_svc.change_plan(
                db, tenant, sub, plan_key=None, seats=rng.choice([0, 100, 220, 300, 500]),
                proration_mode="immediate", actor=a,
            )
    # optional deferred (next_period) change — folded at rollover
    has_deferred = rng.random() < 0.5
    if has_deferred:
        await billing_svc.change_plan(
            db, tenant, sub, plan_key=None, seats=rng.choice([50, 120]),
            proration_mode="next_period", actor=a,
        )
    # Backdate the whole period 40 days, staggering the changes inside it.
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
    changes = (
        (
            await db.execute(
                select(SubscriptionChange)
                .where(SubscriptionChange.subscription_id == sub.id)
                .order_by(SubscriptionChange.id)
            )
        )
        .scalars()
        .all()
    )
    day = 3
    for ch in changes:
        if ch.proration_mode == "immediate":
            ch.effective_at = period.period_start + _td(days=day)
            day += rng.randint(2, 7)
        else:
            ch.effective_at = period.period_end
    await db.flush()

    def lines_key(lines):
        return sorted((li.line_type, li.amount_minor) for li in lines)

    inv1 = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv1 is not None, f"seed {seed}: first close produced no invoice"
    lines1 = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == inv1.id)))
        .scalars()
        .all()
    )
    sub_after_close = (sub.plan_version_id, sub.seat_quantity)

    await billing_svc.void_invoice(db, inv1, reason="fuzz redo", actor=a)
    inv2 = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv2 is not None, f"seed {seed}: re-close produced no invoice"
    lines2 = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == inv2.id)))
        .scalars()
        .all()
    )
    assert lines_key(lines1) == lines_key(lines2), (
        f"seed {seed} (changes={n_changes}, deferred={has_deferred}): "
        f"re-close diverged\n  first : {lines_key(lines1)}\n  second: {lines_key(lines2)}"
    )
    assert inv2.total_minor == inv1.total_minor, f"seed {seed}: totals diverged"
    await db.refresh(sub)
    assert (sub.plan_version_id, sub.seat_quantity) == sub_after_close, (
        f"seed {seed}: sub state after re-close differs from after the original close"
    )


@pytest.mark.parametrize("seed", (301, 313, 337))
async def test_reclose_lines_stable_even_with_forward_changes(db, seed):
    """I5b: forward (post-void) immediate changes belong to the NEXT period's
    segment walk — they may change the fold outcome (supersede) but must NOT
    change THIS period's re-closed lines: the arrears basis, live seats and
    in-period prorations are historical facts the snapshot replays."""
    from datetime import timedelta as _td

    from app.controlplane.models.billing import (
        BillingPeriod,
        InvoiceLine,
        SubscriptionChange,
    )
    from app.controlplane.services import billing as billing_svc
    from app.controlplane.services.billing import _add_interval

    rng = random.Random(seed)
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    a = Actor(user_id=user.id, type="platform")
    sub, _ = await billing_svc.start_subscription(
        db, tenant, plan_key="school", interval="month", seats=rng.choice([0, 250]),
        provider="manual", actor=a,
    )
    for _ in range(rng.randint(0, 2)):
        await billing_svc.change_plan(
            db, tenant, sub, plan_key=None, seats=rng.choice([100, 300, 450]),
            proration_mode="immediate", actor=a,
        )
    if rng.random() < 0.6:
        await billing_svc.change_plan(
            db, tenant, sub, plan_key=None, seats=60, proration_mode="next_period", actor=a
        )
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
    day = 4
    for ch in (
        (
            await db.execute(
                select(SubscriptionChange)
                .where(SubscriptionChange.subscription_id == sub.id)
                .order_by(SubscriptionChange.id)
            )
        )
        .scalars()
        .all()
    ):
        if ch.proration_mode == "immediate":
            ch.effective_at = period.period_start + _td(days=day)
            day += 5
        else:
            ch.effective_at = period.period_end
    await db.flush()

    def lines_key(lines):
        return sorted((li.line_type, li.amount_minor) for li in lines)

    inv1 = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv1 is not None
    lines1 = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == inv1.id)))
        .scalars()
        .all()
    )
    await billing_svc.void_invoice(db, inv1, reason="fuzz fw", actor=a)
    # FORWARD changes in the reopened gap window (effective now > period_end)
    for _ in range(rng.randint(1, 2)):
        await billing_svc.change_plan(
            db, tenant, sub, plan_key=None, seats=rng.choice([80, 200, 350]),
            proration_mode="immediate", actor=a,
        )
    inv2 = await billing_svc.close_period_and_invoice(db, period.id)
    assert inv2 is not None
    lines2 = (
        (await db.execute(select(InvoiceLine).where(InvoiceLine.invoice_id == inv2.id)))
        .scalars()
        .all()
    )
    assert lines_key(lines1) == lines_key(lines2), (
        f"seed {seed}: forward changes altered the RE-CLOSED period's lines\n"
        f"  first : {lines_key(lines1)}\n  second: {lines_key(lines2)}"
    )
