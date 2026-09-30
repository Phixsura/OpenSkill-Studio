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
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.models.outbox import enqueue
from app.controlplane.worker import register_handler
from app.experiments.models import Experiment, ExperimentVersion

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


@register_handler("exp.evaluate_guardrails")
async def handle_evaluate_guardrails(db: AsyncSession, payload: dict) -> None:
    from app.experiments.services.guardrails import GuardrailService

    summary = await GuardrailService(db).evaluate_experiment(payload["experiment_id"])
    if summary.get("breaches"):
        log.warning("exp_guardrail_sweep_paused", **summary)


GUARDRAIL_SWEEP_CAP = 50


async def sweep_experiment_guardrails(
    db: AsyncSession, *, cap: int = GUARDRAIL_SWEEP_CAP
) -> int:
    """Enqueue guardrail evaluation for running experiments, oldest-checked
    first (nulls first) up to cap — the handler stamps last_guardrail_check_at
    so a backlog can never starve any experiment (§106.26 fairness law)."""
    q = (
        select(Experiment.id)
        .where(Experiment.status == "running")
        .order_by(Experiment.last_guardrail_check_at.asc().nulls_first(), Experiment.id.asc())
        .limit(cap)
    )
    enqueued = 0
    for (experiment_id,) in (await db.execute(q)).all():
        enqueue(db, "exp.evaluate_guardrails", {"experiment_id": experiment_id})
        enqueued += 1
    return enqueued


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
    # The analysis-close filter lives in SQL, BEFORE the cap: a backlog of
    # analytically-closed experiments must never occupy capped slots and
    # starve live ones (the fourth accumulation-bomb shape, §106.26 class).
    q = (
        select(Experiment.id)
        .where(
            Experiment.status.in_(_SNAPSHOT_STATUSES),
            or_(
                Experiment.analysis_close_at.is_(None),
                Experiment.analysis_close_at > now,
            ),
        )
        .order_by(Experiment.id.asc())
        .limit(cap)
    )
    enqueued = 0
    for (experiment_id,) in (await db.execute(q)).all():
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


CLOSURE_SWEEP_CAP = 200


async def sweep_experiment_closures(
    db: AsyncSession, *, now: datetime | None = None, cap: int = CLOSURE_SWEEP_CAP
) -> int:
    """Auto-complete running experiments past their spec's stop_policy
    max_days (ADR-017 §13). Completing is always safe (it only stops NEW
    enrollment and stamps ended_at/analysis_close_at) — promotion stays a
    human decision. Bounded oldest-first; the transition is serialized by
    the locked state machine, so a racing manual transition simply wins."""
    from app.experiments.schemas import ExperimentSpec
    from app.experiments.services.experiments import ExperimentService
    from app.experiments.services.guardrails import _system_actor

    now = now or datetime.now(UTC)
    rows = (
        await db.execute(
            select(Experiment.id, Experiment.started_at, Experiment.current_version)
            .where(Experiment.status == "running", Experiment.started_at.is_not(None))
            .order_by(Experiment.started_at.asc())
            .limit(cap)
        )
    ).all()
    closed = 0
    for experiment_id, started_at, current_version in rows:
        version = (
            await db.execute(
                select(ExperimentVersion).where(
                    ExperimentVersion.experiment_id == experiment_id,
                    ExperimentVersion.version == current_version,
                )
            )
        ).scalar_one_or_none()
        if version is None:
            continue
        max_days = ExperimentSpec.model_validate(version.spec).stop_policy.max_days
        if started_at + timedelta(days=max_days) > now:
            continue
        await ExperimentService(db).transition(
            experiment_id,
            to_status="completed",
            actor=_system_actor(),
            reason=f"stop_policy.max_days ({max_days}) elapsed",
        )
        closed += 1
        log.info("exp_auto_completed", experiment_id=experiment_id, max_days=max_days)
    return closed
