"""Experiments outbox topic handlers + sweeps (ADR-017 §13).

Reuses the control-plane transactional-outbox worker. Topics:

  exp.compute_snapshots   {experiment_id, window_start, window_end}  (ISO-8601)

Every handler is idempotent (snapshot writes are UPSERTs on the window's
unique key) — at-least-once delivery and double-enqueued sweeps are safe.
Sweeps are bounded and fairness-capped (the §106.26 accumulation-bomb law:
caps must price in DB lifetime, oldest-first ordering prevents starvation).
"""

from datetime import UTC, datetime, time, timedelta

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.outbox import enqueue
from app.controlplane.worker import register_handler
from app.experiments.models import Experiment

log = structlog.get_logger()

# Snapshots keep computing through pause (guardrails need data) and after
# completion until analysis_close_at (Part I long-term outcomes)
_SNAPSHOT_STATUSES = ("running", "paused", "completed", "analyzed")

SWEEP_CAP = 500


@register_handler("exp.compute_snapshots")
async def handle_compute_snapshots(db: AsyncSession, payload: dict) -> None:
    from app.experiments.services.metrics import MetricService

    window_start = datetime.fromisoformat(payload["window_start"])
    window_end = datetime.fromisoformat(payload["window_end"])
    written = await MetricService(db).compute_experiment_window(
        payload["experiment_id"], window_start=window_start, window_end=window_end
    )
    log.info(
        "exp_snapshots_computed",
        experiment_id=payload["experiment_id"],
        window_start=payload["window_start"],
        written=written,
    )


def previous_utc_day(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now or datetime.now(UTC)
    today = datetime.combine(now.date(), time.min, tzinfo=UTC)
    return today - timedelta(days=1), today


async def sweep_experiment_windows(
    db: AsyncSession, *, now: datetime | None = None, cap: int = SWEEP_CAP
) -> int:
    """Enqueue yesterday's UTC-day snapshot window for every experiment still
    in its analysis life. Bounded; handler idempotency absorbs double-enqueue."""
    now = now or datetime.now(UTC)
    window_start, window_end = previous_utc_day(now)
    q = (
        select(Experiment.id)
        .where(
            Experiment.status.in_(_SNAPSHOT_STATUSES),
        )
        .order_by(Experiment.id.asc())
        .limit(cap)
    )
    enqueued = 0
    for (experiment_id,) in (await db.execute(q)).all():
        exp = await db.get(Experiment, experiment_id)
        if exp.analysis_close_at is not None and exp.analysis_close_at <= now:
            continue
        enqueue(
            db,
            "exp.compute_snapshots",
            {
                "experiment_id": experiment_id,
                "window_start": window_start.isoformat(),
                "window_end": window_end.isoformat(),
            },
        )
        enqueued += 1
    return enqueued
