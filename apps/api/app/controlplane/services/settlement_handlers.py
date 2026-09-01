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
    actual = sum(r.billable_amount_minor for r in rated_rows)

    if status == "cancelled" and actual == 0:
        await credit_svc.release(db, reservation.id)
        log.info("cp_reservation_released", run_id=run_id)
    else:
        await credit_svc.settle(db, reservation.id, int(actual))
        # R38/C11+C35: mark these rows 'settled' so close_period_and_invoice's
        # usage-line query (status == 'rated') no longer picks them up. Without
        # this, credit-enforced usage was BOTH debited from the credit balance
        # here AND billed again on the period invoice — a double charge. A
        # credit reservation IS the payment for that usage; the invoice must
        # not re-bill it.
        settled_ids = [r.id for r in rated_rows]
        if settled_ids:
            await db.execute(
                update(RatedUsage)
                .where(RatedUsage.id.in_(settled_ids), RatedUsage.status == "rated")
                .values(status="settled")
            )
        log.info("cp_reservation_settled", run_id=run_id, actual=int(actual))
