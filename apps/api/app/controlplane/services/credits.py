"""Credit ledger + reservations (ADR-014 §5.2).

All balance mutations run through one critical section: FOR UPDATE on the
(tenant, currency) balance row, invariant check, ledger append with
balance_after, balance update. The DB CHECK constraint backstops races.
"""

from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
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
        dup = (
            await db.execute(
                select(CreditLedgerEntry.id)
                .where(CreditLedgerEntry.idempotency_key == idempotency_key)
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
        # Already terminal — idempotent no-op for retried handlers
        existing = await db.get(CreditReservation, reservation_id)
        if existing is None:
            raise AppError("RESERVATION_CONFLICT", "Reservation not found", 404)
        return existing
    reservation = await db.get(CreditReservation, reservation_id)
    balance = await _locked_balance(db, reservation.tenant_id, reservation.currency)
    balance.reserved_minor = max(0, balance.reserved_minor - reservation.amount_minor)
    if actual_minor > 0:
        chargeable = min(actual_minor, balance.balance_minor)
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
        still_running = False
        if reservation.reference_type == "workflow_run":
            from app.models.workflow_run import RunStatus, WorkflowRun

            run = await db.get(WorkflowRun, reservation.reference_id)
            still_running = run is not None and run.status in (
                RunStatus.PENDING,
                RunStatus.RUNNING,
                RunStatus.WAITING_REVIEW,
            )
        if still_running and reservation.extension_count < 2:
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
        balance = await _locked_balance(db, lot.tenant_id, lot.currency)
        expire_amount = min(lot.amount_minor, balance.balance_minor)
        if expire_amount > 0:
            entry = await _append_entry(
                db,
                balance,
                entry_type="expiration",
                amount_minor=-expire_amount,
                reference_type="promotional_lot",
                reference_id=lot.id,
                idempotency_key=f"expire:{lot.id}",
            )
            if entry is not None:
                lot.consumed_expiration_id = entry.id
                expired += 1
        else:
            lot.consumed_expiration_id = lot.id  # nothing left to expire; mark done
    await db.flush()
    return expired


# ── Run estimation (reservation sizing) ──────────────────────


async def estimate_run_cost_minor(db: AsyncSession, definition: dict, org_id: str) -> int:
    """Rough reservation estimate: Σ provider_action steps × resolved offering
    cost × global markup. Missing data → 0 for that step (pure best-effort)."""
    from decimal import Decimal as D

    from app.models.provider import ProviderConnection, ProviderModelOffering

    total = D(0)
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
            total += D(str(offering.cost_per_call_usd))
    # Global fallback markup mirrors the seeded cost+50% policy
    return int(total * 100 * D("1.5"))
