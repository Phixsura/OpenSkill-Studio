"""Ecosystem outbox topic handlers (ADR-016 Part R).

Reuses the control-plane transactional-outbox worker: business writes enqueue
eco.* topics; the shared worker dispatches them here. Every handler is
idempotent (keyed on natural ids) so at-least-once delivery is safe. Tests
drive handlers inline via process_outbox_once (established pattern).

Topics:
  eco.sync_source          {source_id}
  eco.run_benchmark        {run_id}
  eco.compute_impact       {change_event_id}
  eco.telemetry_window     {window_start, window_end}  (ISO-8601)
  eco.generate_candidates  {entity_kind, entity_id}
"""

from datetime import datetime

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.worker import register_handler
from app.exceptions import AppError

log = structlog.get_logger()


@register_handler("eco.sync_source")
async def handle_sync_source(db: AsyncSession, payload: dict) -> None:
    from app.ecosystem.services.sync import SyncService

    source_id = payload.get("source_id")
    if not source_id:
        return
    try:
        await SyncService(db).run_sync(source_id)
    except AppError as exc:
        # Paused/rate-limited sources are expected states, not worker failures
        if exc.code in (
            "ECO_SOURCE_PAUSED",
            "ECO_RATE_LIMITED",
            "ECO_SYNC_IN_PROGRESS",
            "NOT_FOUND",
        ):
            log.info("eco_sync_skipped", source_id=source_id, code=exc.code)
            return
        raise


@register_handler("eco.run_benchmark")
async def handle_run_benchmark(db: AsyncSession, payload: dict) -> None:
    from app.ecosystem.models.benchmark import BenchmarkRun
    from app.ecosystem.services.benchmark import BenchmarkService

    run_id = payload.get("run_id")
    if not run_id:
        return
    run = await db.get(BenchmarkRun, run_id)
    if run is None or run.status != "queued":
        return  # idempotent: already executed or gone
    await BenchmarkService(db).execute_run(run_id)


@register_handler("eco.compute_impact")
async def handle_compute_impact(db: AsyncSession, payload: dict) -> None:
    from app.ecosystem.models.graph import ImpactAnalysis
    from app.ecosystem.services.impact import ImpactService

    change_event_id = payload.get("change_event_id")
    if not change_event_id:
        return
    # R128: at-least-once outbox + concurrent consumers — the SELECT-then-
    # insert dedupe below loses the race between two workers holding the same
    # redelivered message. Serialize per change event (an advisory lock, not
    # a unique constraint: admin recompute legitimately adds fresh analyses).
    from sqlalchemy import text as _text

    await db.execute(
        _text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": f"eco-impact:{change_event_id}"},
    )
    existing = await db.scalar(
        select(ImpactAnalysis).where(ImpactAnalysis.change_event_id == change_event_id)
    )
    if existing is not None:
        return  # idempotent
    try:
        await ImpactService(db).compute(change_event_id)
    except AppError as exc:
        if exc.code in ("ECO_MERGE_CONFIRMATION_REQUIRED", "NOT_FOUND"):
            log.info("eco_impact_skipped", change_event_id=change_event_id, code=exc.code)
            return
        raise


@register_handler("eco.telemetry_window")
async def handle_telemetry_window(db: AsyncSession, payload: dict) -> None:
    from app.ecosystem.services.telemetry import TelemetryService

    try:
        window_start = datetime.fromisoformat(payload["window_start"])
        window_end = datetime.fromisoformat(payload["window_end"])
    except (KeyError, ValueError):
        return
    svc = TelemetryService(db)
    snapshots = await svc.aggregate_workflow_runs(
        window_start=window_start, window_end=window_end
    )
    # §3.7 other direction: fresh cross-tenant production numbers are compared
    # against the latest completed benchmark for the same target
    from app.ecosystem.services.benchmark import latest_dimension_scores

    for snap in snapshots:
        if snap.org_id is not None:
            continue  # only cross-tenant aggregates drive public divergence
        scores = await latest_dimension_scores(db, snap.entity_kind, snap.entity_id)
        if scores:
            scores.pop("dimension_stats", None)
            await svc.detect_divergence(
                snap.entity_kind, snap.entity_id, benchmark_scores=scores
            )


@register_handler("eco.notify_watchers")
async def handle_notify_watchers(db: AsyncSession, payload: dict) -> None:
    """Fan a change event out to everyone watching the affected entity —
    StatusGator-grade: watching means being told, not having to poll.
    Idempotent per (watcher, change): a notification carrying the same
    change_event_id is not re-created."""
    from app.ecosystem.models.observation import ChangeEvent
    from app.ecosystem.models.replacement import WatchItem, Watchlist
    from app.models.notification import Notification
    from app.services.notification import NotificationService

    change_event_id = payload.get("change_event_id")
    if not change_event_id:
        return
    change = await db.get(ChangeEvent, change_event_id)
    if change is None or not change.canonical_entity_id:
        return
    # R129: same race class as compute_impact — the per-(watcher, change)
    # notification dedupe is SELECT-then-insert; serialize concurrent
    # consumers of a redelivered message per change event
    from sqlalchemy import text as _text

    await db.execute(
        _text("SELECT pg_advisory_xact_lock(hashtext(:key))"),
        {"key": f"eco-notify:{change_event_id}"},
    )
    from datetime import UTC, datetime

    from app.ecosystem.models.observation import SEVERITY_RANK

    change_rank = SEVERITY_RANK.get(change.severity, 0)
    now = datetime.now(UTC)
    candidate_rows = await db.execute(
        select(Watchlist.owner_id, Watchlist.min_severity, Watchlist.muted_until)
        .join(WatchItem, WatchItem.watchlist_id == Watchlist.id)
        .where(WatchItem.target_id == change.canonical_entity_id)
        .distinct()
    )
    # §24 noise controls: below-threshold or snoozed lists don't push. A user
    # notifies if ANY of their watching lists is loud enough and not muted.
    eligible: set[str] = set()
    for owner_id, min_severity, muted_until in candidate_rows:
        if muted_until is not None:
            mu = muted_until if muted_until.tzinfo else muted_until.replace(tzinfo=UTC)
            if mu > now:
                continue
        if change_rank >= SEVERITY_RANK.get(min_severity or "info", 0):
            eligible.add(owner_id)
    watcher_rows = [(owner_id,) for owner_id in sorted(eligible)]
    # §13: org-scoped watchlists also fan out over the org's webhook
    # subscriptions (StatusGator/GitHub posture: watching means being CALLED,
    # not just having an in-app bell). Delivery is the webhook service's
    # fail-safe, entitlement-gated, SSRF-guarded path.
    org_candidates = await db.execute(
        select(Watchlist.org_id, Watchlist.min_severity, Watchlist.muted_until)
        .join(WatchItem, WatchItem.watchlist_id == Watchlist.id)
        .where(
            WatchItem.target_id == change.canonical_entity_id,
            Watchlist.org_id.isnot(None),
        )
        .distinct()
    )
    # §24 applies to org fan-out too (R119): a muted or below-threshold org
    # watchlist must not fire the org webhook — same rule as user pushes
    org_ids: set[str] = set()
    for org_id, min_severity, muted_until in org_candidates:
        if muted_until is not None:
            mu = muted_until if muted_until.tzinfo else muted_until.replace(tzinfo=UTC)
            if mu > now:
                continue
        if change_rank >= SEVERITY_RANK.get(min_severity or "info", 0):
            org_ids.add(org_id)
    org_rows = [(org_id,) for org_id in sorted(org_ids)]
    webhook_payload = {
        "change_event_id": change.id,
        "change_type": change.change_type,
        "field": change.field,
        "severity": change.severity,
        "entity_kind": change.entity_kind,
        "entity_id": change.canonical_entity_id,
        "old_value": change.old_value,
        "new_value": change.new_value,
        "detected_at": change.detected_at.isoformat() if change.detected_at else None,
    }
    from app.services.webhook import WebhookService

    webhook_svc = WebhookService(db)
    for (org_id,) in org_rows:
        await webhook_svc.trigger_event(org_id, "ecosystem.change", webhook_payload)
    svc = NotificationService(db)
    for (owner_id,) in watcher_rows:
        existing = await db.scalar(
            select(Notification.id)
            .where(
                Notification.user_id == owner_id,
                Notification.type == "ecosystem_change",
                Notification.data["change_event_id"].as_string() == change.id,
            )
            .limit(1)
        )
        if existing:
            continue  # at-least-once delivery, exactly-once notification
        await svc.create(
            user_id=owner_id,
            notification_type="ecosystem_change",
            title=f"[{change.severity}] {change.change_type} change: {change.field}",
            body=f"A watched {change.entity_kind or 'entity'} changed ({change.field}).",
            data={
                "change_event_id": change.id,
                "entity_kind": change.entity_kind,
                "entity_id": change.canonical_entity_id,
                "severity": change.severity,
            },
        )
    await db.flush()


async def sweep_due_sources(db: AsyncSession) -> int:
    """CONTINUOUS discovery (the epic's first word): enqueue eco.sync_source
    for every active source whose sync_interval has elapsed. Idempotent —
    the sync handler re-checks status/rate limits, and last_sync_at is
    stamped by the sync itself, so a double-enqueued source syncs once and
    rate-limits the other."""
    from datetime import UTC, datetime, timedelta

    from app.controlplane.models.outbox import enqueue
    from app.ecosystem.models.source import EcosystemSource

    now = datetime.now(UTC)
    rows = await db.scalars(
        select(EcosystemSource).where(EcosystemSource.status == "active")
    )
    enqueued = 0
    for source in rows:
        due_at = (
            source.last_sync_at + timedelta(minutes=source.sync_interval_minutes)
            if source.last_sync_at
            else now
        )
        if due_at <= now:
            enqueue(db, "eco.sync_source", {"source_id": source.id})
            enqueued += 1
    await db.flush()
    return enqueued


async def sweep_stuck_runs(db: AsyncSession, *, max_running_hours: int = 4) -> int:
    """A worker that dies mid-claim leaves a run in `running` forever — the
    fence prevents re-execution but nothing closes the run. Mark runs stuck
    for > max_running_hours as failed (ECO_RUN_STUCK) so the queue metric
    drains and the operator sees an actionable state instead of a zombie.
    Conditional UPDATE: a run that completes concurrently is left alone."""
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import update

    from app.ecosystem.models.benchmark import BenchmarkRun

    cutoff = datetime.now(UTC) - timedelta(hours=max_running_hours)
    result = await db.execute(
        update(BenchmarkRun)
        .where(
            BenchmarkRun.status == "running",
            BenchmarkRun.started_at.isnot(None),
            BenchmarkRun.started_at < cutoff,
        )
        .values(
            status="failed",
            error="ECO_RUN_STUCK: worker died mid-run; results partial, safe to re-queue",
            finished_at=datetime.now(UTC),
        )
    )
    await db.flush()
    return result.rowcount or 0


async def sweep_rollout_evaluations(db: AsyncSession) -> dict:
    """LaunchDarkly auto-check bar: re-evaluate every running/evaluating
    rollout plan on a schedule so guardrail breaches surface without an
    operator remembering to click Evaluate. Detection only — promote/rollback
    remains an explicit human decision (§11.4). A NEW guardrail regression
    notifies platform admins once per regression set (fingerprint stamp)."""
    import hashlib
    import json

    from sqlalchemy.orm.attributes import flag_modified

    from app.ecosystem.models.replacement import RolloutPlan
    from app.ecosystem.services.rollout import RolloutService
    from app.models.user import User, UserRole
    from app.services.notification import NotificationService

    plans = list(
        await db.scalars(
            select(RolloutPlan).where(RolloutPlan.status.in_(("running", "evaluating")))
        )
    )
    if not plans:
        return {"evaluated": 0, "alerted": 0}
    svc = RolloutService(db)
    notify = NotificationService(db)
    admin_ids = [
        row for row in await db.scalars(select(User.id).where(User.role == UserRole.ADMIN))
    ]
    evaluated = 0
    alerted = 0
    for plan in plans:
        # Capture the stamp BEFORE evaluate — evaluation rebuilds comparison
        # from scratch, so reading it afterwards would always see None
        prior_stamp = (plan.comparison or {}).get("alerted_fingerprint")
        try:
            plan = await svc.evaluate(plan.id)
        except Exception:  # noqa: BLE001 — one bad plan never blocks the sweep
            continue
        evaluated += 1
        regressions = (plan.comparison or {}).get("regressions") or []
        if not regressions:
            continue
        fingerprint = hashlib.sha256(
            json.dumps(sorted(regressions)).encode()
        ).hexdigest()[:16]
        comparison = dict(plan.comparison or {})
        if prior_stamp == fingerprint:
            comparison["alerted_fingerprint"] = fingerprint  # keep it sticky
            plan.comparison = comparison
            flag_modified(plan, "comparison")
            continue  # this exact regression set was already announced
        comparison["alerted_fingerprint"] = fingerprint
        plan.comparison = comparison
        flag_modified(plan, "comparison")
        for admin_id in admin_ids:
            await notify.create(
                user_id=admin_id,
                notification_type="ecosystem_rollout_guardrail",
                title=f"Rollout guardrail regression: {', '.join(regressions)}",
                body=(
                    f"Rollout plan {plan.id} shows guarded regressions on "
                    f"{', '.join(regressions)}. Promote stays blocked until resolved."
                ),
                data={"rollout_plan_id": plan.id, "regressions": regressions},
            )
        alerted += 1
    await db.flush()
    return {"evaluated": evaluated, "alerted": alerted}


async def sweep_overdue_impacts(db: AsyncSession) -> int:
    """SLA escalation (PagerDuty/Jira bar): an OPEN impact analysis past its
    deadline notifies every platform admin exactly once (escalated_at stamp
    in summary makes the sweep idempotent). Escalation never mutates the
    analysis status — closing it stays a human decision."""
    from datetime import UTC, datetime

    from sqlalchemy.orm.attributes import flag_modified

    from app.ecosystem.models.graph import ImpactAnalysis
    from app.models.user import User, UserRole
    from app.services.notification import NotificationService

    now = datetime.now(UTC)
    rows = list(
        await db.scalars(
            select(ImpactAnalysis).where(
                ImpactAnalysis.status == "open",
                ImpactAnalysis.deadline_at.isnot(None),
                ImpactAnalysis.deadline_at < now,
            )
        )
    )
    overdue = [a for a in rows if not (a.summary or {}).get("escalated_at")]
    if not overdue:
        return 0
    admin_ids = [
        row for row in await db.scalars(select(User.id).where(User.role == UserRole.ADMIN))
    ]
    svc = NotificationService(db)
    for analysis in overdue:
        summary = dict(analysis.summary or {})
        summary["escalated_at"] = now.isoformat()
        analysis.summary = summary
        flag_modified(analysis, "summary")
        deadline = analysis.deadline_at
        if deadline is not None and deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=UTC)
        overdue_hours = round((now - deadline).total_seconds() / 3600, 1) if deadline else None
        for admin_id in admin_ids:
            await svc.create(
                user_id=admin_id,
                notification_type="ecosystem_impact_sla",
                title=f"Impact analysis overdue: {analysis.classification}",
                body=(
                    f"Impact {analysis.id} on {analysis.root_kind} has been open "
                    f"past its deadline ({overdue_hours}h overdue)."
                ),
                data={
                    "impact_analysis_id": analysis.id,
                    "classification": analysis.classification,
                    "deadline_at": deadline.isoformat() if deadline else None,
                },
            )
    await db.flush()
    return len(overdue)


async def prune_ecosystem_history(db: AsyncSession, *, now=None) -> dict:
    """§16 retention: bounded operational history without losing evidence.

    - Availability STATUS probes: raw rows older than 90 days are pruned,
      keeping each entity's latest row. Status FLIPS are permanently preserved
      as append-only availability_changed observations + change events, so no
      transition history is lost — only redundant "still fine" samples.
    - Source sync-run audit rows: pruned after 180 days (observations they
      produced are append-only and permanent; sync_run_id is SET NULL by FK).
    The observation/change ledgers are NEVER pruned (Part B: append-only).
    """
    from datetime import UTC, datetime, timedelta

    from sqlalchemy import delete, func

    from app.ecosystem.models.mapping import AvailabilityRecord
    from app.ecosystem.models.source import SourceSyncRun

    now = now or datetime.now(UTC)
    status_cutoff = now - timedelta(days=90)
    latest_per_entity = (
        select(
            AvailabilityRecord.entity_kind,
            AvailabilityRecord.entity_id,
            func.max(AvailabilityRecord.observed_at).label("latest"),
        )
        .where(AvailabilityRecord.record_type == "status")
        .group_by(AvailabilityRecord.entity_kind, AvailabilityRecord.entity_id)
        .subquery()
    )
    stale_status = await db.execute(
        delete(AvailabilityRecord).where(
            AvailabilityRecord.record_type == "status",
            AvailabilityRecord.observed_at < status_cutoff,
            ~select(latest_per_entity.c.latest)
            .where(
                latest_per_entity.c.entity_kind == AvailabilityRecord.entity_kind,
                latest_per_entity.c.entity_id == AvailabilityRecord.entity_id,
                latest_per_entity.c.latest == AvailabilityRecord.observed_at,
            )
            .exists(),
        )
    )
    sync_cutoff = now - timedelta(days=180)
    old_runs = await db.execute(
        delete(SourceSyncRun).where(SourceSyncRun.started_at < sync_cutoff)
    )
    await db.flush()
    from sqlalchemy import delete as sa_delete

    from app.ecosystem.models.source import RawSnapshot

    snap_cutoff = (now or datetime.now(UTC)) - timedelta(days=90)
    snap_result = await db.execute(
        sa_delete(RawSnapshot).where(RawSnapshot.fetched_at < snap_cutoff)
    )
    pruned_snapshots = snap_result.rowcount or 0
    # R153: price observations grow unboundedly (one row per sync per unit).
    # Undecided (unreviewed) rows older than 180 days are noise — the latest
    # ones drive estimates and the trend window is 90 days. DECIDED rows
    # (approved/rejected) are audit evidence for billing mints and are kept.
    from app.ecosystem.models.mapping import PriceObservation

    price_cutoff = now - timedelta(days=180)
    old_prices = await db.execute(
        sa_delete(PriceObservation).where(
            PriceObservation.reconciliation_status == "unreviewed",
            PriceObservation.observed_at < price_cutoff,
        )
    )
    return {
        "availability_status_pruned": stale_status.rowcount or 0,
        "sync_runs_pruned": old_runs.rowcount or 0,
        "raw_snapshots_pruned": pruned_snapshots,
        "unreviewed_prices_pruned": old_prices.rowcount or 0,
    }


@register_handler("eco.check_availability")
async def handle_check_availability(db: AsyncSession, payload: dict) -> None:
    """§11.3: availability probed independently of catalog syncs."""
    from app.ecosystem.services.pricing import AvailabilityService

    entity_kind, entity_id = payload.get("entity_kind"), payload.get("entity_id")
    if not entity_kind or not entity_id:
        return
    try:
        await AvailabilityService(db).probe_status(entity_kind, entity_id)
    except AppError as exc:
        if exc.code in ("NOT_FOUND", "VALIDATION_ERROR"):
            log.info("eco_availability_skipped", entity_id=entity_id, code=exc.code)
            return
        raise


@register_handler("eco.generate_candidates")
async def handle_generate_candidates(db: AsyncSession, payload: dict) -> None:
    from app.ecosystem.services.replacement import ReplacementService

    entity_kind, entity_id = payload.get("entity_kind"), payload.get("entity_id")
    if not entity_kind or not entity_id:
        return
    try:
        await ReplacementService(db).generate_candidates(
            deprecated_kind=entity_kind, deprecated_id=entity_id
        )
    except AppError as exc:
        if exc.code in ("VALIDATION_ERROR", "NOT_FOUND"):
            log.info("eco_candidates_skipped", entity_id=entity_id, code=exc.code)
            return
        raise
