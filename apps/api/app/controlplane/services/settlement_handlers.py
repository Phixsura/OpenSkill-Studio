"""Outbox handlers tying reservations to run outcomes (ADR-014 §5.3)."""

import structlog
from sqlalchemy import func, select
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

    actual = (
        await db.execute(
            select(func.coalesce(func.sum(RatedUsage.billable_amount_minor), 0))
            .select_from(RatedUsage)
            .join(UsageEvent, UsageEvent.id == RatedUsage.usage_event_id)
            .where(
                UsageEvent.workflow_run_id == run_id,
                RatedUsage.billable_currency == reservation.currency,
                RatedUsage.status.in_(["rated", "invoiced"]),
            )
        )
    ).scalar_one()

    if status == "cancelled" and actual == 0:
        await credit_svc.release(db, reservation.id)
        log.info("cp_reservation_released", run_id=run_id)
    else:
        await credit_svc.settle(db, reservation.id, int(actual))
        log.info("cp_reservation_settled", run_id=run_id, actual=int(actual))
