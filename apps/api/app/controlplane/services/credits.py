"""Credit ledger + reservations (ADR-014 §5.2).

All balance mutations run through one critical section: FOR UPDATE on the
(tenant, currency) balance row, invariant check, ledger append with
balance_after, balance update. The DB CHECK constraint backstops races.
"""

from datetime import UTC, datetime, timedelta
from decimal import Decimal

import structlog
from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.controlplane.models.credit import (
    CREDIT_ENTRY_TYPES,
    CreditLedgerEntry,
    CreditReservation,
    TenantCreditBalance,
)
from app.controlplane.services.audit import Actor, record_audit
from app.exceptions import AppError

log = structlog.get_logger()


async def _locked_balance(db: AsyncSession, tenant_id: str, currency: str) -> TenantCreditBalance:
    """Ensure-and-lock the balance row — THE serialization point."""
    await db.execute(
        pg_insert(TenantCreditBalance)
        .values(tenant_id=tenant_id, currency=currency, balance_minor=0, reserved_minor=0)
        .on_conflict_do_nothing(index_elements=["tenant_id", "currency"])
    )
    return (
        await db.execute(
            select(TenantCreditBalance)
            .where(
                TenantCreditBalance.tenant_id == tenant_id,
                TenantCreditBalance.currency == currency,
            )
            .with_for_update()
            # populate_existing forces the ORM to overwrite a cached identity-map
            # copy with the freshly-locked row bytes. Without it, a caller that
            # read this balance UNLOCKED earlier in the same session (e.g.
            # close_period_and_invoice computing credit_available) would keep the
            # stale copy even though FOR UPDATE returned newer values — a
            # concurrently-committed top-up/debit would be silently overwritten
            # (lost update) and the ledger balance_after chain would stop
            # replaying. This is THE serialization point; it must read fresh.
            .execution_options(populate_existing=True)
        )
    ).scalar_one()


async def _append_entry(
    db: AsyncSession,
    balance: TenantCreditBalance,
    *,
    entry_type: str,
    amount_minor: int,
    reference_type: str | None = None,
    reference_id: str | None = None,
    reason: str | None = None,
    expires_at: datetime | None = None,
    idempotency_key: str | None = None,
    created_by: str | None = None,
) -> CreditLedgerEntry | None:
    """Ledger append + balance update inside the caller's critical section.
    Returns None when the idempotency key already exists (no-op)."""
    if entry_type not in CREDIT_ENTRY_TYPES:
        raise AppError("VALIDATION_ERROR", f"Unknown entry type '{entry_type}'", 422)
    if idempotency_key is not None:
        # Scope the dedup by tenant: idempotency keys are per-tenant, and a
        # client-supplied key on POST /platform/tenants/{id}/credits/adjust
        # shares this namespace with internal namespaced keys. An unscoped
        # check let the same client key on tenant B match tenant A's entry and
        # silently drop B's adjustment (or 500 on the old global unique index).
        dup = (
            await db.execute(
                select(CreditLedgerEntry.id)
                .where(
                    CreditLedgerEntry.tenant_id == balance.tenant_id,
                    CreditLedgerEntry.idempotency_key == idempotency_key,
                )
                .limit(1)
            )
        ).scalar_one_or_none()
        if dup is not None:
            return None
    new_balance = balance.balance_minor + amount_minor
    if new_balance < 0:
        raise AppError("INSUFFICIENT_CREDIT", "Insufficient credit balance", 402)
    if new_balance < balance.reserved_minor:
        raise AppError("INSUFFICIENT_CREDIT", "Balance cannot drop below reserved amount", 402)
    entry = CreditLedgerEntry(
        tenant_id=balance.tenant_id,
        currency=balance.currency,
        entry_type=entry_type,
        amount_minor=amount_minor,
        balance_after_minor=new_balance,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        expires_at=expires_at,
        idempotency_key=idempotency_key,
        created_by=created_by,
    )
    db.add(entry)
    balance.balance_minor = new_balance
    await db.flush()
    return entry


# ── Public mutations ─────────────────────────────────────────


async def top_up(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    reference_type: str | None = None,
    reference_id: str | None = None,
    idempotency_key: str | None = None,
    actor: Actor,
) -> CreditLedgerEntry | None:
    if amount_minor <= 0:
        raise AppError("VALIDATION_ERROR", "Top-up amount must be positive", 422)
    balance = await _locked_balance(db, tenant_id, currency)
    entry = await _append_entry(
        db,
        balance,
        entry_type="purchase",
        amount_minor=amount_minor,
        reference_type=reference_type,
        reference_id=reference_id,
        idempotency_key=idempotency_key,
        created_by=actor.user_id,
    )
    if entry is not None:
        await record_audit(
            db,
            actor=actor,
            action="credit.topped_up",
            target_type="tenant",
            target_id=tenant_id,
            tenant_id=tenant_id,
            after={"amount_minor": amount_minor, "currency": currency},
        )
    return entry


async def grant_promotional(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    expires_at: datetime,
    reason: str,
    actor: Actor,
) -> CreditLedgerEntry:
    if amount_minor <= 0:
        raise AppError("VALIDATION_ERROR", "Grant amount must be positive", 422)
    balance = await _locked_balance(db, tenant_id, currency)
    entry = await _append_entry(
        db,
        balance,
        entry_type="promotional",
        amount_minor=amount_minor,
        reason=reason,
        expires_at=expires_at,
        created_by=actor.user_id,
    )
    await record_audit(
        db,
        actor=actor,
        action="credit.promotional_granted",
        target_type="tenant",
        target_id=tenant_id,
        tenant_id=tenant_id,
        after={"amount_minor": amount_minor, "expires_at": expires_at.isoformat()},
        reason=reason,
    )
    return entry


async def refund(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    reference_type: str,
    reference_id: str,
    reason: str,
    actor: Actor,
    idempotency_key: str | None = None,
) -> CreditLedgerEntry | None:
    if amount_minor <= 0:
        raise AppError("VALIDATION_ERROR", "Refund amount must be positive", 422)
    balance = await _locked_balance(db, tenant_id, currency)
    entry = await _append_entry(
        db,
        balance,
        entry_type="refund",
        amount_minor=amount_minor,
        reference_type=reference_type,
        reference_id=reference_id,
        reason=reason,
        idempotency_key=idempotency_key,
        created_by=actor.user_id,
    )
    if entry is not None:
        await record_audit(
            db,
            actor=actor,
            action="credit.refunded",
            target_type=reference_type,
            target_id=reference_id,
            tenant_id=tenant_id,
            after={"amount_minor": amount_minor},
            reason=reason,
        )
    return entry


async def adjust(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    reason: str,
    actor: Actor,
    idempotency_key: str | None = None,
) -> CreditLedgerEntry | None:
    """Signed manual adjustment (platform billing_admin only, audited)."""
    if amount_minor == 0:
        raise AppError("VALIDATION_ERROR", "Adjustment amount cannot be zero", 422)
    balance = await _locked_balance(db, tenant_id, currency)
    entry = await _append_entry(
        db,
        balance,
        entry_type="adjustment",
        amount_minor=amount_minor,
        reason=reason,
        idempotency_key=idempotency_key,
        created_by=actor.user_id,
    )
    if entry is not None:
        await record_audit(
            db,
            actor=actor,
            action="credit.adjusted",
            target_type="tenant",
            target_id=tenant_id,
            tenant_id=tenant_id,
            after={"amount_minor": amount_minor, "currency": currency},
            reason=reason,
        )
    return entry


async def debit(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    reference_type: str,
    reference_id: str,
    idempotency_key: str | None = None,
    created_by: str | None = None,
) -> CreditLedgerEntry | None:
    """Direct spend against AVAILABLE balance (balance − reserved)."""
    if amount_minor <= 0:
        raise AppError("VALIDATION_ERROR", "Debit amount must be positive", 422)
    balance = await _locked_balance(db, tenant_id, currency)
    available = balance.balance_minor - balance.reserved_minor
    if available < amount_minor:
        raise AppError("INSUFFICIENT_CREDIT", "Insufficient available credit", 402)
    return await _append_entry(
        db,
        balance,
        entry_type="usage_debit",
        amount_minor=-amount_minor,
        reference_type=reference_type,
        reference_id=reference_id,
        idempotency_key=idempotency_key,
        created_by=created_by,
    )


# ── Reservations (reserve → settle/release) ──────────────────


async def reserve(
    db: AsyncSession,
    tenant_id: str,
    currency: str,
    amount_minor: int,
    *,
    reference_type: str,
    reference_id: str,
) -> CreditReservation:
    """Hold available credit. Idempotent per (reference_type, reference_id)
    while held — a duplicate reserve returns the existing hold."""
    if amount_minor <= 0:
        raise AppError("VALIDATION_ERROR", "Reservation amount must be positive", 422)
    existing = (
        await db.execute(
            select(CreditReservation).where(
                CreditReservation.reference_type == reference_type,
                CreditReservation.reference_id == reference_id,
                CreditReservation.status == "held",
            )
        )
    ).scalar_one_or_none()
    if existing is not None:
        return existing
    balance = await _locked_balance(db, tenant_id, currency)
    available = balance.balance_minor - balance.reserved_minor
    if available < amount_minor:
        raise AppError("INSUFFICIENT_CREDIT", "Insufficient available credit to reserve", 402)
    reservation = CreditReservation(
        tenant_id=tenant_id,
        currency=currency,
        amount_minor=amount_minor,
        reference_type=reference_type,
        reference_id=reference_id,
        expires_at=datetime.now(UTC) + timedelta(hours=settings.reservation_ttl_hours),
    )
    db.add(reservation)
    balance.reserved_minor += amount_minor
    await db.flush()
    return reservation


async def require_available(db: AsyncSession, tenant_id: str, currency: str) -> None:
    """Assert the tenant has SOME available (unreserved) credit in `currency`.

    Used by credit-enforced runs whose cost estimate rounds to 0 (NULL-cost
    offerings) — we can't size a reservation, but a prepay tenant with zero
    balance must not start a run that will incur billable usage (R31/C13).
    Raises INSUFFICIENT_CREDIT (402) when nothing is available.
    """
    balance = await _locked_balance(db, tenant_id, currency)
    if balance.balance_minor - balance.reserved_minor <= 0:
        raise AppError(
            "INSUFFICIENT_CREDIT",
            "No available credit for this run under credit enforcement",
            402,
        )


async def settle(db: AsyncSession, reservation_id: str, actual_minor: int) -> CreditReservation:
    """held → settled; debit ACTUAL usage only (issue §16 — a failed provider
    call must not consume the estimate). actual may exceed the hold but is
    floored at the remaining balance (shortfall logged, no debt rows in v1)."""
    if actual_minor < 0:
        raise AppError("VALIDATION_ERROR", "Settled amount cannot be negative", 422)
    result = await db.execute(
        update(CreditReservation)
        .where(CreditReservation.id == reservation_id, CreditReservation.status == "held")
        .values(
            status="settled",
            settled_amount_minor=actual_minor,
            settled_at=datetime.now(UTC),
        )
    )
    if not result.rowcount:
        # Already terminal — idempotent no-op for retried handlers. Return the
        # row with its TRUE current status (populate_existing defeats a stale
        # identity-map copy) so callers can tell a real settle from a reservation
        # the expiry cron already released out from under us (R51: marking usage
        # 'settled' after a release charges it nowhere).
        existing = (
            await db.execute(
                select(CreditReservation)
                .where(CreditReservation.id == reservation_id)
                .execution_options(populate_existing=True)
            )
        ).scalar_one_or_none()
        if existing is None:
            raise AppError("RESERVATION_CONFLICT", "Reservation not found", 404)
        return existing
    reservation = (
        await db.execute(
            select(CreditReservation)
            .where(CreditReservation.id == reservation_id)
            .execution_options(populate_existing=True)
        )
    ).scalar_one()
    balance = await _locked_balance(db, reservation.tenant_id, reservation.currency)
    balance.reserved_minor = max(0, balance.reserved_minor - reservation.amount_minor)
    if actual_minor > 0:
        # Floor the charge at what's AVAILABLE after releasing this run's own
        # hold — i.e. balance minus the holds still outstanding for OTHER
        # reservations. Flooring at balance_minor alone (ignoring reserved_minor)
        # let an overage charge drop the balance below the other holds, which
        # _append_entry hard-rejects with INSUFFICIENT_CREDIT 402 — settle() is
        # supposed to never fail (issue §16), so that 402 dead-lettered the
        # run.terminal handler. available >= this run's hold always, so a
        # within-estimate settle is unaffected; only overage is capped.
        available = balance.balance_minor - balance.reserved_minor
        chargeable = min(actual_minor, max(0, available))
        if chargeable < actual_minor:
            log.warning(
                "cp_settle_shortfall",
                reservation_id=reservation.id,
                actual=actual_minor,
                charged=chargeable,
            )
        if chargeable > 0:
            await _append_entry(
                db,
                balance,
                entry_type="reservation_settle",
                amount_minor=-chargeable,
                reference_type=reservation.reference_type,
                reference_id=reservation.reference_id,
                idempotency_key=f"settle:{reservation.id}",
                reason=(
                    f"shortfall {actual_minor - chargeable}" if chargeable < actual_minor else None
                ),
            )
    await db.flush()
    return reservation


async def release(db: AsyncSession, reservation_id: str) -> CreditReservation:
    """held → released; frees the hold with no charge."""
    result = await db.execute(
        update(CreditReservation)
        .where(CreditReservation.id == reservation_id, CreditReservation.status == "held")
        .values(status="released", released_at=datetime.now(UTC))
    )
    if not result.rowcount:
        existing = await db.get(CreditReservation, reservation_id)
        if existing is None:
            raise AppError("RESERVATION_CONFLICT", "Reservation not found", 404)
        return existing
    reservation = await db.get(CreditReservation, reservation_id)
    balance = await _locked_balance(db, reservation.tenant_id, reservation.currency)
    balance.reserved_minor = max(0, balance.reserved_minor - reservation.amount_minor)
    await db.flush()
    return reservation


async def expire_stale_reservations(db: AsyncSession) -> int:
    """Worker cron: held past expiry. Referenced run still RUNNING → extend
    (max 2×6h); otherwise release."""
    now = datetime.now(UTC)
    stale = (
        (
            await db.execute(
                select(CreditReservation).where(
                    CreditReservation.status == "held",
                    CreditReservation.expires_at < now,
                )
            )
        )
        .scalars()
        .all()
    )
    handled = 0
    for reservation in stale:
        run = None
        if reservation.reference_type == "workflow_run":
            from app.models.workflow_run import RunStatus, WorkflowRun

            run = await db.get(WorkflowRun, reservation.reference_id)

        # R31/C9: a run parked at a review gate legitimately waits up to
        # settings.review_due_days (1–30d) — the bounded 2×6h extension used
        # to release its hold at ~36h, so on approval the run resumed with no
        # reservation and its usage went uncharged. Keep extending a
        # WAITING_REVIEW run indefinitely (the gate is the natural bound; a
        # review-expiry/ cancel emits run.terminal which settles). Keep the
        # small bounded extension only for PENDING/RUNNING, which should never
        # linger — a genuinely stuck executor is then released as before.
        if run is not None and run.status == RunStatus.WAITING_REVIEW:
            reservation.extension_count += 1
            reservation.expires_at = now + timedelta(hours=24)
        elif (
            run is not None
            and run.status in (RunStatus.PENDING, RunStatus.RUNNING)
            and reservation.extension_count < 2
        ):
            reservation.extension_count += 1
            reservation.expires_at = now + timedelta(hours=6)
        else:
            await release(db, reservation.id)
        handled += 1
    return handled


async def expire_promotional(db: AsyncSession) -> int:
    """Daily cron: expired unconsumed promo lots → negative expiration entries.

    v1 simplification (ADR): consumption is not lot-tracked; the expired
    amount = min(lot face value, current balance). Ledger stays replayable —
    consumed_expiration_id marks processed lots so reruns are no-ops.
    """
    now = datetime.now(UTC)
    lots = (
        (
            await db.execute(
                select(CreditLedgerEntry).where(
                    CreditLedgerEntry.entry_type == "promotional",
                    CreditLedgerEntry.expires_at.is_not(None),
                    CreditLedgerEntry.expires_at < now,
                    CreditLedgerEntry.consumed_expiration_id.is_(None),
                )
            )
        )
        .scalars()
        .all()
    )
    expired = 0
    for lot in lots:
        # Isolate each lot in a SAVEPOINT: one tenant whose lot can't be expired
        # (or any other per-lot error) must not abort the whole platform-wide
        # daily cron and retry forever. A failed lot is left unconsumed and
        # retried on the next run.
        try:
            async with db.begin_nested():
                balance = await _locked_balance(db, lot.tenant_id, lot.currency)
                # Expire at most the UNRESERVED balance: reserved credit is
                # spoken for by a live hold, and _append_entry rejects any entry
                # that would drop balance below reserved (402). Promo credit that
                # is currently reserved simply isn't expired this pass — the hold
                # will settle/release and a later cron run expires the remainder
                # (the lot stays unconsumed until fully handled).
                available = balance.balance_minor - balance.reserved_minor
                # R98[H10]: a PARTIAL expiry (reserved remainder) left the lot
                # open, but the fixed idempotency key 'expire:{lot.id}' made
                # every later pass a dedup no-op — the remainder never
                # expired (wedged forever as spendable credit). Track what
                # this lot already expired (sum of its expiration entries)
                # and key each pass by that cumulative offset — distinct per
                # pass, stable across crash-retries of the SAME pass.
                already_expired = int(
                    (
                        await db.execute(
                            select(
                                func.coalesce(func.sum(-CreditLedgerEntry.amount_minor), 0)
                            ).where(
                                CreditLedgerEntry.entry_type == "expiration",
                                CreditLedgerEntry.reference_type == "promotional_lot",
                                CreditLedgerEntry.reference_id == lot.id,
                            )
                        )
                    ).scalar_one()
                )
                remaining_face = max(lot.amount_minor - already_expired, 0)
                expire_amount = min(remaining_face, max(0, available))
                if remaining_face <= 0:
                    lot.consumed_expiration_id = lot.id  # fully expired earlier
                elif expire_amount > 0:
                    entry = await _append_entry(
                        db,
                        balance,
                        entry_type="expiration",
                        amount_minor=-expire_amount,
                        reference_type="promotional_lot",
                        reference_id=lot.id,
                        idempotency_key=f"expire:{lot.id}:{already_expired}",
                    )
                    # Fully consumed only when the cumulative expiry reaches
                    # the face value; partial leaves it open for a later pass.
                    if entry is not None and already_expired + expire_amount >= lot.amount_minor:
                        lot.consumed_expiration_id = entry.id
                    expired += 1
                elif balance.balance_minor <= 0:
                    lot.consumed_expiration_id = lot.id  # nothing left; mark done
        except Exception:  # noqa: BLE001 — one bad lot must not wedge the cron
            log.warning("cp_promo_expiry_lot_failed", lot_id=lot.id, exc_info=True)
            continue
    await db.flush()
    return expired


# ── Run estimation (reservation sizing) ──────────────────────


async def estimate_run_cost_minor(
    db: AsyncSession, definition: dict, org_id: str, currency: str = "USD"
) -> int:
    """Rough reservation estimate, in minor units of `currency` (the tenant's
    balance currency the hold will be placed against).

    Σ provider_action steps × resolved offering cost (USD) × global markup,
    then FX-converted to `currency` and scaled by that currency's minor
    multiplier. Missing data → 0 for that step (pure best-effort). Offering
    cost_per_call_usd is a USD amount; a hold sized in USD-cents but placed
    against a non-USD balance under-reserved by the FX factor (e.g. ~1300× for
    KRW), so the conversion is mandatory."""
    from app.controlplane.models.pricing import minor_multiplier
    from app.models.provider import ProviderConnection, ProviderModelOffering

    from .rating import resolve_fx

    total_usd = Decimal(0)
    for step in definition.get("steps", []):
        if step.get("type") != "provider_action":
            continue
        capability = step.get("config", {}).get("capability", "")
        offering = (
            await db.execute(
                select(ProviderModelOffering)
                .join(
                    ProviderConnection,
                    ProviderConnection.id == ProviderModelOffering.connection_id,
                )
                .where(
                    ProviderConnection.org_id == org_id,
                    ProviderModelOffering.capability_key == capability,
                    ProviderModelOffering.is_active.is_(True),
                    ProviderModelOffering.cost_per_call_usd.is_not(None),
                )
                .order_by(ProviderModelOffering.cost_per_call_usd.desc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if offering is not None and offering.cost_per_call_usd is not None:
            total_usd += Decimal(str(offering.cost_per_call_usd))
    # Global fallback markup mirrors the seeded cost+50% policy.
    total_usd *= Decimal("1.5")
    if total_usd <= 0:
        return 0
    # Convert USD major → tenant currency major, then to minor units. A missing
    # FX rate falls back to a 1:1 factor (best-effort estimate; the run.terminal
    # settle reconciles ACTUAL usage in tenant currency regardless).
    if currency != "USD":
        fx = await resolve_fx(db, "USD", currency, datetime.now(UTC))
        rate = fx[0] if fx is not None else Decimal(1)
    else:
        rate = Decimal(1)
    return int(total_usd * rate * minor_multiplier(currency))
