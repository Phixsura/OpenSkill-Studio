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
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

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


@register_handler("exp.apply_promotion")
async def handle_apply_promotion(db: AsyncSession, payload: dict) -> None:
    """Async promotion apply (§18): typed failures land in apply_error and
    return the draft to 'approved' (retryable); crashes propagate for outbox
    retry. The system actor never approves — it only executes an approval."""
    from app.experiments.services.promotion import PromotionService
    from app.models.user import User

    actor = await db.get(User, payload["actor_user_id"])
    if actor is None:  # approver deleted between queue and run — leave parked
        log.error("exp_apply_actor_missing", draft_id=payload["draft_id"])
        return
    draft = await PromotionService(db).finish_async_apply(payload["draft_id"], actor=actor)
    if draft.apply_error:
        log.warning(
            "exp_async_apply_failed",
            draft_id=draft.id,
            apply_error=draft.apply_error,
        )


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


INTERACTION_MIN_SHARED = 100
INTERACTION_PAIR_CAP = 20
_INTERACTION_REALERT_HOURS = 7 * 24


async def sweep_experiment_interactions(
    db: AsyncSession, *, cap_pairs: int = INTERACTION_PAIR_CAP, now: datetime | None = None
) -> int:
    """Cross-experiment interaction scan (ADR-017 §4.13 v2, weekly).

    Layers guarantee mutual exclusion WITHIN a layer, but a unit can live in
    experiments of different layers simultaneously — if the two variant
    assignments are not independent over the shared units, both analyses are
    confounded. Deterministic hashing makes true dependence impossible by
    construction, so a significant chi-square here means something is broken
    (a salt collision, a targeting overlap artifact, a migration replaying
    assignments) and both owners should know. Alert-only on BOTH sides,
    7-day suppression per pair, pair-capped per run.
    """
    from itertools import combinations

    from app.experiments.models import ExperimentAssignment, GuardrailEvent
    from app.experiments.models.guardrail import INTERACTION_GUARDRAIL_KEY
    from app.experiments.services.analysis import chi2_sf

    running = (
        await db.execute(
            select(
                Experiment.id, Experiment.key, Experiment.layer_key,
                Experiment.owner_user_id, Experiment.title,
            )
            .where(Experiment.status == "running")
            .order_by(Experiment.id.asc())
        )
    ).all()
    a = aliased(ExperimentAssignment)
    b = aliased(ExperimentAssignment)
    # §106.26 fairness: a fixed-order cap starves the tail pairs forever —
    # rotate the capped window by ISO week so every pair gets its turn
    cross_layer_pairs = [
        (x, y)
        for x, y in combinations(running, 2)
        if x[2] != y[2]  # same layer = mutually exclusive by construction
    ]
    if not cross_layer_pairs:
        return 0
    start = (now or datetime.now(UTC)).isocalendar().week % len(cross_layer_pairs)
    window = (cross_layer_pairs + cross_layer_pairs)[start : start + cap_pairs]
    alerts = 0
    for (id1, key1, _layer1, owner1, title1), (id2, key2, _layer2, owner2, title2) in window:
        rows = (
            await db.execute(
                select(a.variant_key, b.variant_key, func.count())
                .select_from(a)
                .join(b, (a.unit_type == b.unit_type) & (a.unit_id == b.unit_id))
                .where(
                    a.experiment_id == id1,
                    b.experiment_id == id2,
                    a.is_holdout.is_(False),
                    b.is_holdout.is_(False),
                )
                .group_by(a.variant_key, b.variant_key)
            )
        ).all()
        table: dict[tuple[str, str], int] = {(v1, v2): n for v1, v2, n in rows}
        total = sum(table.values())
        if total < INTERACTION_MIN_SHARED:
            continue
        rows_keys = sorted({v1 for v1, _ in table})
        cols_keys = sorted({v2 for _, v2 in table})
        df = (len(rows_keys) - 1) * (len(cols_keys) - 1)
        if df < 1:
            continue
        row_tot = {r: sum(table.get((r, c), 0) for c in cols_keys) for r in rows_keys}
        col_tot = {c: sum(table.get((r, c), 0) for r in rows_keys) for c in cols_keys}
        chi2 = 0.0
        for r in rows_keys:
            for c in cols_keys:
                expected = row_tot[r] * col_tot[c] / total
                if expected <= 0:
                    continue
                chi2 += (table.get((r, c), 0) - expected) ** 2 / expected
        if chi2_sf(chi2, df) >= 0.001:
            continue
        # 7-day suppression per PAIR (checked on side 1; both write together)
        recent = (
            await db.execute(
                select(GuardrailEvent.detail).where(
                    GuardrailEvent.experiment_id == id1,
                    GuardrailEvent.guardrail_key == INTERACTION_GUARDRAIL_KEY,
                    GuardrailEvent.created_at
                    >= datetime.now(UTC) - timedelta(hours=_INTERACTION_REALERT_HOURS),
                )
            )
        ).scalars()
        if any((d or {}).get("with") == id2 for d in recent):
            continue
        base = {"chi2": round(chi2, 3), "df": df, "shared_units": total}
        db.add(
            GuardrailEvent(
                experiment_id=id1,
                guardrail_key=INTERACTION_GUARDRAIL_KEY,
                action="alerted",
                auto=True,
                detail={**base, "with": id2, "with_key": key2},
            )
        )
        db.add(
            GuardrailEvent(
                experiment_id=id2,
                guardrail_key=INTERACTION_GUARDRAIL_KEY,
                action="alerted",
                auto=True,
                detail={**base, "with": id1, "with_key": key1},
            )
        )
        alerts += 1
        log.warning(
            "exp_interaction_alert", experiment_a=key1, experiment_b=key2, **base
        )
        # defect #38: both owners hear about it once per dedup window
        try:
            from app.services.notification import NotificationService

            for owner_id, title, other_key in (
                (owner1, title1, key2), (owner2, title2, key1),
            ):
                await NotificationService(db).create(
                    user_id=owner_id,
                    notification_type="experiment_guardrail",
                    title=f"Interaction alert on '{title}'",
                    body=(
                        f"Variant assignments correlate with experiment "
                        f"'{other_key}' — randomization integrity suspect."
                    ),
                    data={"experiment_a": id1, "experiment_b": id2, **base},
                )
        except Exception:  # noqa: BLE001 — additive, never blocking
            log.warning("exp_interaction_notify_failed", experiment_a=id1)
    return alerts


EXPOSURE_RETENTION_DAYS = 400
PRUNE_BATCH_CAP = 50_000


async def prune_experiment_history(
    db: AsyncSession, *, now: datetime | None = None, cap: int = PRUNE_BATCH_CAP
) -> dict:
    """Retention (ADR-017 §13, deviation documented in §18): raw exposures of
    ARCHIVED experiments older than 400 days are DELETED (no cold table yet)
    — their aggregates live on in metric snapshots, and archived experiments
    are outside every analysis path. Live/terminal-but-analyzable experiments
    keep their full exposure trail. Batch-capped (oldest first via ULID id)."""
    from sqlalchemy import delete

    from app.experiments.models import ExperimentExposure

    now = now or datetime.now(UTC)
    cutoff = now - timedelta(days=EXPOSURE_RETENTION_DAYS)
    target_ids = (
        select(ExperimentExposure.id)
        .join(Experiment, Experiment.id == ExperimentExposure.experiment_id)
        .where(Experiment.status == "archived", ExperimentExposure.occurred_at < cutoff)
        .order_by(ExperimentExposure.id.asc())
        .limit(cap)
        .scalar_subquery()
    )
    result = await db.execute(
        delete(ExperimentExposure).where(ExperimentExposure.id.in_(target_ids))
    )
    pruned = result.rowcount or 0
    if pruned:
        log.info("exp_exposures_pruned", count=pruned)
    return {"exposures": pruned}


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
        try:
            max_days = ExperimentSpec.model_validate(version.spec).stop_policy.max_days
        except Exception:  # noqa: BLE001 — one poison spec must not stall the batch
            log.error("exp_closure_spec_unparseable", experiment_id=experiment_id)
            continue
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
