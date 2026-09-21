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
        if exc.code in ("ECO_SOURCE_PAUSED", "ECO_RATE_LIMITED", "NOT_FOUND"):
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
    await TelemetryService(db).aggregate_workflow_runs(
        window_start=window_start, window_end=window_end
    )


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
