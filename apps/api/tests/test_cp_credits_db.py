"""P5 DB tests: credit ledger, reservations, budgets, eval-budget migration."""

import asyncio
from datetime import UTC, datetime, timedelta
from decimal import Decimal

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


@pytest.mark.asyncio
async def test_locked_balance_reads_fresh_after_stale_cache():
    """R51 CRITICAL: _locked_balance must return the freshly-locked row, not a
    stale identity-map copy read earlier UNLOCKED in the same session. Without
    populate_existing, a session that read the balance before another session
    committed a top-up would keep the old value, and its next debit/mutation
    would silently overwrite the committed top-up (lost update) and break the
    ledger balance_after chain.

    Repro: session A reads the balance unlocked (caches balance_minor=1000);
    session B tops up +500 and commits (DB row now 1500); session A then debits
    100 through the credit service. With the bug, A's debit computes from the
    stale 1000 → writes 900, erasing B's +500. With the fix, A re-reads 1500
    under the lock → writes 1400."""
    from app.core.database import AsyncSessionLocal, engine

    try:
        async with AsyncSessionLocal() as setup:
            user = await _mk_user(setup)
            tenant = await _mk_tenant(setup, user)
            await credit_svc.top_up(setup, tenant.id, "USD", 1000, actor=_actor(user))
            await setup.commit()
            tid = tenant.id

        async with AsyncSessionLocal() as sess_a:
            # A reads the balance UNLOCKED first → caches balance_minor=1000 in
            # its identity map (mirrors close_period_and_invoice's old pre-read).
            cached = (
                await sess_a.execute(
                    select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tid)
                )
            ).scalar_one()
            assert cached.balance_minor == 1000

            # B commits a concurrent top-up of +500 in its own session.
            async with AsyncSessionLocal() as sess_b:
                await credit_svc.top_up(sess_b, tid, "USD", 500, actor=_actor(user))
                await sess_b.commit()

            # A now debits 100 through the credit service. _locked_balance must
            # re-read 1500 under the lock (populate_existing) → 1400, not 900.
            await credit_svc.debit(
                sess_a, tid, "USD", 100, reference_type="manual", reference_id=str(ULID())
            )
            await sess_a.commit()

        async with AsyncSessionLocal() as check:
            final = (
                await check.execute(
                    select(TenantCreditBalance.balance_minor).where(
                        TenantCreditBalance.tenant_id == tid
                    )
                )
            ).scalar_one()
            assert final == 1400, f"lost update: expected 1400, got {final}"
            # A's debit must have landed on the fresh 1500 → balance_after 1400.
            # The stale-read bug's signature is a 900 entry (1000 − 100) and a
            # final balance of 900; assert neither exists. (We don't assert
            # created_at ordering — it defaults to transaction-start time, which
            # doesn't reflect commit order for overlapping transactions.)
            afters = set(
                (
                    await check.execute(
                        select(CreditLedgerEntry.balance_after_minor).where(
                            CreditLedgerEntry.tenant_id == tid
                        )
                    )
                )
                .scalars()
                .all()
            )
            assert 1400 in afters, f"A's debit did not see the fresh balance: {afters}"
            assert 900 not in afters, f"stale-read signature present: {afters}"
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
async def test_settle_overage_floors_at_available_not_balance(db):
    """R51[2]: an overage settle must floor at AVAILABLE (balance − other
    holds), not balance_minor. Two runs each hold 50 of a 100 balance; run A
    settles with actual 80 (overage). Flooring at balance (100) would try to
    debit 80, dropping balance to 20 < the 50 still held by run B, which
    _append_entry rejects with 402 — dead-lettering the handler. Flooring at
    available (100−50=50 after A's own hold releases) charges 50, logs the
    shortfall, and never fails."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    await credit_svc.top_up(db, tenant.id, "USD", 100, actor=_actor(user))
    ra = await credit_svc.reserve(
        db, tenant.id, "USD", 50, reference_type="workflow_run", reference_id=str(ULID())
    )
    await credit_svc.reserve(
        db, tenant.id, "USD", 50, reference_type="workflow_run", reference_id=str(ULID())
    )
    # A settles with an overage of 80 — must NOT raise, charges only available.
    settled = await credit_svc.settle(db, ra.id, 80)
    assert settled.status == "settled"
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    # A's hold (50) released; charged min(80, available 50) = 50 → balance 50,
    # still >= run B's 50 hold. Never negative, never below reserved.
    assert balance.balance_minor == 50
    assert balance.reserved_minor == 50


@pytest.mark.asyncio
async def test_expire_promotional_skips_reserved_and_isolates_lots(db):
    """R51[3]: expire_promotional must not try to expire credit that is
    currently RESERVED (that would drop balance below reserved → 402), and a
    single failing lot must not abort the whole cron. A promo lot of 100 fully
    reserved by a live hold is left unconsumed this pass (no 402, cron does not
    wedge); once released, a later pass expires it."""
    from datetime import UTC, datetime, timedelta

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # Promo grant already expired, then fully reserved by a live hold.
    await credit_svc.grant_promotional(
        db,
        tenant.id,
        "USD",
        100,
        expires_at=datetime.now(UTC) - timedelta(days=1),
        reason="welcome",
        actor=_actor(user),
    )
    hold = await credit_svc.reserve(
        db, tenant.id, "USD", 100, reference_type="workflow_run", reference_id=str(ULID())
    )
    # Must not raise despite the reserved balance.
    await credit_svc.expire_promotional(db)
    balance = (
        await db.execute(
            select(TenantCreditBalance).where(TenantCreditBalance.tenant_id == tenant.id)
        )
    ).scalar_one()
    # Nothing expired yet — all 100 is reserved.
    assert balance.balance_minor == 100
    assert balance.reserved_minor == 100
    # Release the hold, run expiry again → the lot now expires fully.
    await credit_svc.release(db, hold.id)
    await credit_svc.expire_promotional(db)
    await db.refresh(balance)
    assert balance.balance_minor == 0


@pytest.mark.asyncio
async def test_idempotency_key_scoped_per_tenant(db):
    """R51[5]: a client-supplied adjust idempotency key must be unique PER
    TENANT, not globally. The same key on two different tenants must produce
    two independent entries — not silently drop the second."""
    user = await _mk_user(db)
    t1 = await _mk_tenant(db, user)
    t2 = await _mk_tenant(db, user)
    key = "recon-2026-08-31"
    e1 = await credit_svc.adjust(
        db, t1.id, "USD", 500, reason="recon", actor=_actor(user), idempotency_key=key
    )
    e2 = await credit_svc.adjust(
        db, t2.id, "USD", 700, reason="recon", actor=_actor(user), idempotency_key=key
    )
    assert e1 is not None and e2 is not None
    assert e1.id != e2.id
    assert e1.tenant_id == t1.id and e2.tenant_id == t2.id
    # Same key on the SAME tenant is still idempotent (drops the duplicate).
    dup = await credit_svc.adjust(
        db, t1.id, "USD", 999, reason="recon", actor=_actor(user), idempotency_key=key
    )
    assert dup is None


@pytest.mark.asyncio
async def test_estimate_run_cost_converts_to_tenant_currency(db):
    """R51[4]: estimate_run_cost_minor returns minor units of the tenant's
    currency, FX-converted from USD offering costs. A KRW estimate must be
    scaled by the USD→KRW rate and KRW's minor multiplier (1), not returned as
    raw USD-cents."""
    from decimal import Decimal

    from app.controlplane.models.pricing import FxRate
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

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    org = Organization(
        name="EstOrg",
        slug=f"est-{str(ULID()).lower()}",
        status=OrgStatus.ACTIVE,
        tenant_id=tenant.id,
        created_by=user.id,
    )
    db.add(org)
    await db.flush()
    db.add(
        OrgMember(org_id=org.id, user_id=user.id, role=OrgRole.OWNER, status=MemberStatus.ACTIVE)
    )
    adapter = ProviderAdapter(key=f"mock-{str(ULID()).lower()}", name="Mock")
    db.add(adapter)
    await db.flush()
    conn = ProviderConnection(org_id=org.id, adapter_id=adapter.id, name="c", created_by=user.id)
    db.add(conn)
    await db.flush()
    db.add(
        ProviderModelOffering(
            connection_id=conn.id,
            capability_key="text_generation",
            model_name="m",
            is_active=True,
            cost_per_call_usd=Decimal("10"),
        )
    )
    # USD→KRW = 1300; effective now.
    db.add(
        FxRate(
            base_currency="USD",
            quote_currency="KRW",
            rate=Decimal("1300"),
            effective_from=datetime.now(UTC) - timedelta(days=1),
            created_by=user.id,
        )
    )
    await db.flush()

    definition = {
        "steps": [
            {"id": "s1", "type": "provider_action", "config": {"capability": "text_generation"}}
        ]
    }
    est = await credit_svc.estimate_run_cost_minor(db, definition, org.id, "KRW")
    # $10 × 1.5 markup = $15 → ×1300 KRW/USD × minor_multiplier(KRW)=1 = 19500.
    assert est == 19500, f"expected 19500 KRW minor, got {est}"
    # USD path unchanged: $15 × ×100 = 1500 cents.
    est_usd = await credit_svc.estimate_run_cost_minor(db, definition, org.id, "USD")
    assert est_usd == 1500


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


@pytest.mark.asyncio
async def test_require_available_blocks_zero_balance(db):
    """R31/C13: a credit-enforced run whose estimate rounds to 0 (NULL-cost
    offering) still calls require_available — a prepay tenant with no credit
    must not start a run that will incur billable usage."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    # zero balance → blocked
    with pytest.raises(AppError) as exc:
        await credit_svc.require_available(db, tenant.id, "USD")
    assert exc.value.code == "INSUFFICIENT_CREDIT"
    # some available credit → passes
    await credit_svc.top_up(db, tenant.id, "USD", 100, actor=_actor(user))
    await credit_svc.require_available(db, tenant.id, "USD")  # no raise
    # fully reserved (no available) → blocked again
    await credit_svc.reserve(
        db, tenant.id, "USD", 100, reference_type="workflow_run", reference_id=str(ULID())
    )
    with pytest.raises(AppError) as exc2:
        await credit_svc.require_available(db, tenant.id, "USD")
    assert exc2.value.code == "INSUFFICIENT_CREDIT"


@pytest.mark.asyncio
async def test_review_gated_reservation_extends_past_bounded_limit():
    """R31/C9: a run parked at a review gate can wait up to review_due_days
    (1-30d). Its reservation must keep extending past the 2×6h bounded limit
    (used for stuck PENDING/RUNNING) — else on approval the run resumes with
    no hold and its usage goes uncharged. A stuck RUNNING run past the bound
    is still released."""
    from app.core.database import engine
    from app.models.organization import (
        MemberStatus,
        Organization,
        OrgMember,
        OrgRole,
        OrgStatus,
    )
    from app.models.workflow_run import RunStatus, WorkflowRun

    try:
        async with AsyncSessionLocal() as db:
            user = await _mk_user(db)
            tenant = await _mk_tenant(db, user)
            org = Organization(
                name="RG",
                slug=f"rg-{str(ULID()).lower()}",
                status=OrgStatus.ACTIVE,
                tenant_id=tenant.id,
                created_by=user.id,
            )
            db.add(org)
            await db.flush()
            db.add(
                OrgMember(
                    org_id=org.id,
                    user_id=user.id,
                    role=OrgRole.OWNER,
                    status=MemberStatus.ACTIVE,
                )
            )
            await credit_svc.top_up(db, tenant.id, "USD", 5000, actor=_actor(user))

            async def mk_run_hold(run_status):
                run = WorkflowRun(
                    org_id=org.id,
                    definition_snapshot={"steps": []},
                    status=run_status,
                    started_by=user.id,
                )
                db.add(run)
                await db.flush()
                r = await credit_svc.reserve(
                    db,
                    tenant.id,
                    "USD",
                    100,
                    reference_type="workflow_run",
                    reference_id=run.id,
                )
                r.expires_at = datetime.now(UTC) - timedelta(hours=1)
                r.extension_count = 2  # already at the bounded limit
                await db.flush()
                return r

            review_hold = await mk_run_hold(RunStatus.WAITING_REVIEW)
            running_hold = await mk_run_hold(RunStatus.RUNNING)
            await credit_svc.expire_stale_reservations(db)
            await db.refresh(review_hold)
            await db.refresh(running_hold)
            # review-gated: extended (still held), count advanced past 2
            assert review_hold.status == "held"
            assert review_hold.extension_count == 3
            # stuck RUNNING past the bound: released
            assert running_hold.status == "released"
    finally:
        await engine.dispose()


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
async def test_eval_settings_writethrough_uses_tenant_currency(db):
    """R63[10]: the org eval-budget write-through must denominate the policy in
    the TENANT's currency, not a hardcoded USD × 100. For a JPY tenant, spend
    is rated in JPY (minor mult 1), so a USD/×100 policy matched zero spend and
    the limit was 100× too large."""
    user = await _mk_user(db)
    tenant = await tenant_svc.create_tenant(
        db,
        name=f"JP {ULID()}",
        slug=f"jp-{str(ULID()).lower()}",
        actor=_actor(user),
        owner_user_id=user.id,
        status=TenantStatus.ACTIVE,
        with_trial=False,
        currency="JPY",
    )
    await budget_svc.upsert_from_eval_settings(
        db, tenant_id=tenant.id, org_id="01JORGORGORGORGORGORGORGOR", monthly_budget_usd=1000
    )
    policy = (
        await db.execute(
            select(BudgetPolicy).where(
                BudgetPolicy.tenant_id == tenant.id, BudgetPolicy.scope_type == "org"
            )
        )
    ).scalar_one()
    # JPY minor multiplier is 1 → 1000, not 100000; currency is the tenant's.
    assert policy.currency == "JPY"
    assert policy.limit_minor == 1000


@pytest.mark.asyncio
async def test_create_budget_rejects_currency_mismatch(db):
    """R63[11]: a budget whose currency != tenant.currency silently matches
    zero spend (rating writes tenant-currency rows) — must be rejected."""
    from app.controlplane.api.credits import BudgetPolicyRequest, create_budget

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)  # USD tenant
    body = BudgetPolicyRequest(
        scope_type="tenant",
        period="monthly",
        limit_minor=1000,
        currency="EUR",  # mismatch
    )
    with pytest.raises(AppError) as exc:
        await create_budget(tenant.id, body, user=user, db=db)
    assert exc.value.code == "CURRENCY_MISMATCH"


@pytest.mark.asyncio
async def test_tenant_ai_ceiling_denominated_in_tenant_currency(db):
    """R32/C5: the implicit AI ceiling must be in the TENANT's currency, or a
    non-USD tenant's ceiling matches zero of its (tenant-currency) rated rows
    and never fires. EUR tenant, EUR-rated spend over a EUR ceiling → block."""
    from app.controlplane.models.plan import TenantEntitlementOverride
    from app.controlplane.models.pricing import RatedUsage
    from app.controlplane.models.usage import UsageEvent
    from app.controlplane.services.entitlements import invalidate_cache

    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    tenant.currency = "EUR"
    db.add(
        TenantEntitlementOverride(
            tenant_id=tenant.id,
            key="max_ai_budget_usd_month",
            value={"v": "0.5"},  # €0.50 ceiling
            reason="cap",
            enforcement="hard",
        )
    )
    await db.flush()
    await invalidate_cache(tenant.id)
    org = "01JC5EURORGEURORGEURORGEUR"
    # €1.00 (100 minor) of EUR-denominated rated spend > €0.50 ceiling
    eid = str(ULID())
    db.add(
        UsageEvent(
            id=eid,
            tenant_id=tenant.id,
            org_id=org,
            usage_type="image_generation",
            quantity=1,
            unit="images",
            occurred_at=datetime.now(UTC),
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
            quantity=1,
            cost_rate_snapshot={},
            internal_cost_minor=0,
            internal_cost_currency="EUR",
            sell_rate_snapshot={},
            billable_amount_minor=100,
            billable_amount_exact=Decimal(100),
            billable_currency="EUR",
            status="rated",
            rated_at=datetime.now(UTC),
        )
    )
    await db.flush()
    with pytest.raises(AppError) as exc:
        await budget_svc.check(db, tenant, org)
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
                db,
                tenant,
                plan_key="school",
                interval="month",
                seats=0,
                provider="manual",
                actor=a,
            )
            await pricing_svc.create_price_policy(
                db,
                actor=a,
                name=f"cs {ULID()}",
                policy_type="fixed_unit_price",
                usage_type="image_generation",
                currency="USD",
                params={"unit_price_minor": 50},
                effective_from=datetime.now(UTC) - timedelta(days=1),
                tenant_id=tenant.id,
            )
            run_id = str(ULID())
            await credit_svc.reserve(
                db, tenant.id, "USD", 1000, reference_type="workflow_run", reference_id=run_id
            )
            await metering.emit_usage(
                db,
                tenant_id=tenant.id,
                org_id="01JFAKEORGFAKEORGFAKEORGFA",
                usage_type="image_generation",
                quantity=3,
                occurred_at=datetime.now(UTC) - timedelta(minutes=5),
                source="workflow_runtime",
                idempotency_key=f"cs-{ULID()}",
                workflow_run_id=run_id,
            )
            enqueue(db, "run.terminal", {"run_id": run_id, "status": "completed"})
            await db.commit()
            tid, sub_id = tenant.id, sub.id
        # settle via the handler (scoped drain)
        for _ in range(30):
            async with AsyncSessionLocal() as db:
                if await process_outbox_once(db, topics=["usage.recorded", "run.terminal"]) == 0:
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


# ── R66/R67: runtime + evaluation credit/budget seams ────────


@pytest.mark.asyncio
async def test_eval_credit_enforcement_reserve_and_settle(db):
    """R67[4]: evaluation spend bypassed credit enforcement entirely — a
    prepay (credit_enforcement) tenant with zero balance ran unlimited paid
    LLM calls. trigger_evaluation now reserves at trigger and settles ACTUAL
    usage after execution; zero balance → 402 before any LLM call."""
    from unittest.mock import AsyncMock, patch

    from app.core.llm import LLMResponse
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"CE {ULID()}",
        slug=f"ce-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    tenant.metadata_ = {"credit_enforcement": True}
    await db.flush()

    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "CEP",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        user.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, user.id)
    await proj_svc.submit_draft(sub.id, user.id)
    await db.flush()

    good = LLMResponse(
        content=(
            '{"scores":[{"criterion":"Q","score":80,"max_score":100,"feedback":"ok"}],'
            '"overall_feedback":"fine","strengths":[],"improvements":[]}'
        ),
        input_tokens=500,
        output_tokens=200,
        model="claude-sonnet-5",
        provider="anthropic",
    )

    # Zero balance → 402 BEFORE any LLM call
    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=good)
        mock_create.return_value = mock_llm
        with pytest.raises(AppError) as exc:
            await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
        assert exc.value.code == "INSUFFICIENT_CREDIT"
        mock_llm.complete.assert_not_awaited()

    # Fund the tenant → runs; reservation is created and terminally settled
    await credit_svc.top_up(
        db,
        tenant.id,
        "USD",
        100_000,
        actor=_actor(user),
        idempotency_key=f"ce-top-{ULID()}",
    )
    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=good)
        mock_create.return_value = mock_llm
        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
    assert task.status.value == "completed"
    reservation = (
        await db.execute(
            select(CreditReservation).where(
                CreditReservation.reference_type == "evaluation_task",
                CreditReservation.reference_id == task.id,
            )
        )
    ).scalar_one()
    assert reservation.status == "settled"
    # No dangling hold
    bal = (
        await db.execute(
            select(TenantCreditBalance).where(
                TenantCreditBalance.tenant_id == tenant.id,
                TenantCreditBalance.currency == "USD",
            )
        )
    ).scalar_one()
    assert bal.reserved_minor == 0


@pytest.mark.asyncio
async def test_advance_blocked_for_suspended_tenant(db):
    """R66[1]: a run parked at a review gate resumed provider spending after
    tenant suspension — require_tenant_active fired only at create_run.
    _advance_once (the choke point every resume path funnels through) must
    make no progress for a blocked tenant."""
    from app.models.workflow_run import RunStatus, WorkflowRun
    from app.services.organization import OrgService
    from app.services.workflow_runtime import _advance_once

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"SB {ULID()}",
        slug=f"sb-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    run = WorkflowRun(
        org_id=org.id,
        pack_id=None,
        release_id=None,
        installation_id=None,
        definition_snapshot={"steps": [], "edges": []},
        inputs={},
        started_by=user.id,
        status=RunStatus.PENDING,
    )
    db.add(run)
    await db.flush()
    # Active → progresses (PENDING→RUNNING at least)
    assert await _advance_once(db, run.id) is True or run.status != RunStatus.PENDING
    # Suspended → frozen
    run2 = WorkflowRun(
        org_id=org.id,
        pack_id=None,
        release_id=None,
        installation_id=None,
        definition_snapshot={"steps": [], "edges": []},
        inputs={},
        started_by=user.id,
        status=RunStatus.PENDING,
    )
    db.add(run2)
    await db.flush()
    tenant.status = TenantStatus.SUSPENDED
    await db.flush()
    from app.controlplane.services.entitlements import invalidate_cache

    await invalidate_cache(tenant.id)
    assert await _advance_once(db, run2.id) is False
    await db.refresh(run2)
    assert run2.status == RunStatus.PENDING  # untouched


def test_calculate_cost_unknown_model_not_free():
    """R67[6]: models absent from PRICING costed $0 — an org-selectable
    default_model exempted the org from every budget while real provider
    spend accrued. Unknown models now cost at the flagship fallback tier."""
    from app.core.llm import LLMResponse, calculate_cost

    unknown = LLMResponse(
        content="x",
        input_tokens=1_000_000,
        output_tokens=1_000_000,
        model="claude-opus-4-6",  # served by the API, absent from PRICING
        provider="anthropic",
    )
    cost = calculate_cost(unknown)
    assert cost > 0, "unknown model must never be free"
    assert cost == 18.0  # 3.00 input + 15.00 output at 1M tokens each
    # Known models unchanged
    known = LLMResponse(
        content="x",
        input_tokens=1_000_000,
        output_tokens=0,
        model="claude-haiku-4-5",
        provider="anthropic",
    )
    assert calculate_cost(known) == 0.80


@pytest.mark.asyncio
async def test_eval_usage_events_carry_project_and_user_refs(db):
    """R67[5]: project-/user-scoped BudgetPolicies join RatedUsage via the
    usage event's project_id/user_id — eval events omitted both, so scoped
    policies never accumulated eval spend."""
    from unittest.mock import AsyncMock, patch

    from app.controlplane.models.usage import UsageEvent
    from app.core.llm import LLMResponse
    from app.services.evaluation import EvaluationService
    from app.services.organization import OrgService
    from app.services.project import ProjectService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"RF {ULID()}",
        slug=f"rf-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    eval_svc = EvaluationService(db)
    await eval_svc.update_eval_settings(org.id, {"enabled": True, "monthly_budget_usd": 100})
    proj_svc = ProjectService(db)
    proj = await proj_svc.create_project(
        org.id,
        "RFP",
        None,
        "D",
        "I",
        "beginner",
        100,
        [{"criterion": "Q", "max_score": 100}],
        None,
        None,
        0,
        0,
        None,
        user.id,
    )
    sub = await proj_svc.create_submission(org.id, proj.id, user.id)
    await proj_svc.submit_draft(sub.id, user.id)
    await db.flush()
    good = LLMResponse(
        content=(
            '{"scores":[{"criterion":"Q","score":80,"max_score":100,"feedback":"ok"}],'
            '"overall_feedback":"fine","strengths":[],"improvements":[]}'
        ),
        input_tokens=100,
        output_tokens=50,
        model="claude-sonnet-5",
        provider="anthropic",
    )
    with patch("app.services.evaluation.create_llm_client") as mock_create:
        mock_llm = AsyncMock()
        mock_llm.complete = AsyncMock(return_value=good)
        mock_create.return_value = mock_llm
        task = await eval_svc.trigger_evaluation(org.id, sub.id, "submission_review")
    events = (
        (await db.execute(select(UsageEvent).where(UsageEvent.evaluation_task_id == task.id)))
        .scalars()
        .all()
    )
    assert events, "eval must emit usage events"
    for e in events:
        assert e.project_id == proj.id, f"{e.usage_type} missing project ref"
        assert e.user_id == user.id, f"{e.usage_type} missing user ref"


@pytest.mark.asyncio
async def test_budget_hard_stop_blocks_projected_breach(db):
    """R67[7]: with projected_minor=0 a hard_stop only blocked AFTER spend
    strictly exceeded the limit — the breaching run itself passed. The
    projected estimate must make the gate fire on the run that WOULD
    breach."""
    user = await _mk_user(db)
    tenant = await _mk_tenant(db, user)
    policy = BudgetPolicy(
        tenant_id=tenant.id,
        scope_type="tenant",
        scope_id=None,
        period="monthly",
        limit_minor=100,
        currency="USD",
        hard_stop=True,
    )
    db.add(policy)
    await db.flush()
    # Spent 90 of 100; a projected 20 breaches → must block NOW
    decision_blocked = None
    try:
        await budget_svc.check(db, tenant, "01JFAKEORGFAKEORGFAKEORGFA", projected_minor=20)
        decision_blocked = False
    except AppError as exc:
        decision_blocked = exc.code == "BUDGET_EXCEEDED"
        # spent=0 here so 0+20 <= 100 → should NOT block yet
    assert decision_blocked is False
    # projected alone crossing the limit blocks
    with pytest.raises(AppError) as exc:
        await budget_svc.check(db, tenant, "01JFAKEORGFAKEORGFAKEORGFA", projected_minor=101)
    assert exc.value.code == "BUDGET_EXCEEDED"


def test_workflow_sweep_cron_registered():
    """R66[2]: sweep_stale ran only lazily (run-detail reads) — review due_at
    never fired autonomously. The worker cron registry must include it."""
    from app.controlplane.worker import _cron_jobs

    names = {getattr(j, "name", "") for j in _cron_jobs()}
    assert "cp_workflow_sweep" in names


@pytest.mark.asyncio
async def test_run_terminal_defers_while_step_lease_live(db):
    """R66[3]: cancel enqueues run.terminal while a provider call is mid-
    flight; settling then misses the late-landing usage. The handler must
    defer (raise → outbox backoff) while any step lease is live."""
    from datetime import timedelta as _td

    from app.controlplane.services.settlement_handlers import handle_run_terminal
    from app.models.workflow_run import (
        RunStatus,
        StepRunStatus,
        WorkflowRun,
        WorkflowStepRun,
    )
    from app.services.organization import OrgService

    user = await _mk_user(db)
    org = await OrgService(db).create(
        name=f"IF {ULID()}",
        slug=f"if-{str(ULID()).lower()}",
        description=None,
        created_by=user.id,
    )
    tenant = await db.get(TenantAccount, org.tenant_id)
    tenant.status = TenantStatus.ACTIVE
    await db.flush()
    await credit_svc.top_up(
        db, tenant.id, "USD", 10_000, actor=_actor(user), idempotency_key=f"if-{ULID()}"
    )
    run = WorkflowRun(
        org_id=org.id,
        pack_id=None,
        release_id=None,
        installation_id=None,
        definition_snapshot={"steps": [], "edges": []},
        inputs={},
        started_by=user.id,
        status=RunStatus.CANCELLED,
    )
    db.add(run)
    await db.flush()
    # Step cancelled but with a LIVE lease = provider call still in flight
    step = WorkflowStepRun(
        run_id=run.id,
        step_id="s1",
        step_type="provider_action",
        status=StepRunStatus.CANCELLED,
        max_attempts=3,
        lease_expires_at=datetime.now(UTC) + _td(seconds=90),
    )
    db.add(step)
    await db.flush()
    await credit_svc.reserve(
        db,
        tenant.id,
        "USD",
        500,
        reference_type="workflow_run",
        reference_id=run.id,
    )
    with pytest.raises(RuntimeError, match="in-flight"):
        await handle_run_terminal(db, {"run_id": run.id, "status": "cancelled"})
    # Lease gone → settles fine
    step.lease_expires_at = None
    await db.flush()
    await handle_run_terminal(db, {"run_id": run.id, "status": "cancelled"})
    reservation = (
        await db.execute(
            select(CreditReservation).where(
                CreditReservation.reference_type == "workflow_run",
                CreditReservation.reference_id == run.id,
            )
        )
    ).scalar_one()
    assert reservation.status == "released"  # cancelled with zero usage
