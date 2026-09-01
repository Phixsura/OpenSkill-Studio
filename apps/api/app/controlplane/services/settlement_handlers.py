"""Outbox handlers tying reservations to run outcomes (ADR-014 §5.3)."""

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.credit import CreditReservation
from app.controlplane.models.pricing import RatedUsage
from app.controlplane.models.usage import UsageEvent
from app.controlplane.services import credits as credit_svc
from app.controlplane.services.rating import rate_pending
from app.controlplane.worker import register_handler

log = structlog.get_logger()


@register_handler("run.terminal")
async def handle_run_terminal(db: AsyncSession, payload: dict) -> None:
    """Settle (or release) the run's credit reservation with ACTUAL usage.

    Idempotent: settle/release are guarded transitions; rating is idempotent.
    A failed provider call settles only what was actually metered (issue §16).
    """
    run_id = payload["run_id"]
    status = payload.get("status", "completed")
    reservation = (
        await db.execute(
            select(CreditReservation).where(
                CreditReservation.reference_type == "workflow_run",
                CreditReservation.reference_id == run_id,
                CreditReservation.status == "held",
            )
        )
    ).scalar_one_or_none()
    if reservation is None:
        return  # tenant without credit enforcement, or already settled

    # Rate this run's events first so actual billable is complete.
    await rate_pending(db, tenant_id=reservation.tenant_id)

    # Select the run's rated rows for the settle sum. Only rows still 'rated'
    # (not yet invoiced/voided) are settleable against the reservation.
    rated_rows = (
        (
            await db.execute(
                select(RatedUsage)
                .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
                .where(
                    UsageEvent.workflow_run_id == run_id,
                    RatedUsage.billable_currency == reservation.currency,
                    RatedUsage.status == "rated",
                )
            )
        )
        .scalars()
        .all()
    )
    # R75: settle the round-of-sum of exact per-event amounts, not the sum of
    # per-event rounded integers (sub-half-minor events would settle as 0).
    from decimal import ROUND_HALF_UP, Decimal

    actual = int(
        sum((Decimal(r.billable_amount_exact) for r in rated_rows), Decimal(0)).quantize(
            Decimal("1"), rounding=ROUND_HALF_UP
        )
    )

    if status == "cancelled" and actual == 0:
        await credit_svc.release(db, reservation.id)
        log.info("cp_reservation_released", run_id=run_id)
    else:
        settled = await credit_svc.settle(db, reservation.id, int(actual))
        # R51: only mark the run's rated rows 'settled' (which excludes them
        # from the period invoice) when settle() ACTUALLY debited the credit
        # balance — i.e. the reservation transitioned held→settled here. If the
        # expiry cron already released the hold (settle is now a no-op that
        # charges nothing), the usage must stay 'rated' so close_period_and_
        # invoice bills it on the invoice instead. Flipping to 'settled' after a
        # release would charge the usage NOWHERE (silent revenue loss).
        if settled.status == "settled":
            settled_ids = [r.id for r in rated_rows]
            if settled_ids:
                await db.execute(
                    update(RatedUsage)
                    .where(RatedUsage.id.in_(settled_ids), RatedUsage.status == "rated")
                    .values(status="settled")
                )
            log.info("cp_reservation_settled", run_id=run_id, actual=int(actual))
        else:
            # Reservation was already released/expired — usage stays billable on
            # the invoice. Log so the mismatch is observable.
            log.warning(
                "cp_reservation_not_settled",
                run_id=run_id,
                reservation_status=settled.status,
                actual=int(actual),
            )
