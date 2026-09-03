"""Control-plane background worker — transactional outbox consumer + crons.

Run:  cd apps/api && uv run arq app.controlplane.worker.WorkerSettings
(Makefile target: make dev-worker)

Design (ADR-014):
- Business writes INSERT cp_outbox rows in the same transaction as the
  business rows, so a committed business fact always has its message.
- This worker polls with FOR UPDATE SKIP LOCKED, dispatches per-topic
  handlers, retries with exponential backoff via available_at, and
  dead-letters (status=failed) after settings.outbox_max_attempts.
- Every handler MUST be idempotent: natural keys / INSERT ON CONFLICT /
  conditional UPDATE. Tests call process_outbox_once(db) directly — no
  Redis or arq needed for DB test suites.

Topic registry is filled in by later phases:
  usage.recorded     → rating (P4)
  run.terminal       → reservation settlement (P5)
  period.close_due   → invoice generation (P6)
  invoice.finalized  → revenue-share accrual (P7)
  purchase.paid      → revenue-share accrual (P7)
  purchase.refunded  → negative accrual (P7)
  fx.rate_created    → unblock blocked rated rows (P4)
  provision.run      → tenant provisioning step machine (P10)
"""

from __future__ import annotations

import socket
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime, timedelta

import structlog
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings

log = structlog.get_logger()

# topic -> async handler(db, payload). Registered by phase modules at import
# time via register_handler(); kept as a plain dict so tests can inspect it.
HANDLERS: dict[str, Callable[[AsyncSession, dict], Awaitable[None]]] = {}


def register_handler(topic: str):
    """Decorator: register an outbox topic handler (idempotency required)."""

    def deco(fn):
        HANDLERS[topic] = fn
        return fn

    return deco


def load_handlers() -> None:
    """Import every handler-bearing module so HANDLERS is fully populated.
    Called by worker startup AND process_outbox_once (tests)."""
    import app.controlplane.services.billing  # noqa: F401
    import app.controlplane.services.provisioning  # noqa: F401
    import app.controlplane.services.rating  # noqa: F401
    import app.controlplane.services.revenue_share  # noqa: F401
    import app.controlplane.services.settlement_handlers  # noqa: F401


def _worker_id() -> str:
    return f"{socket.gethostname()}:{id(HANDLERS) & 0xFFFF}"


def _now() -> datetime:
    return datetime.now(UTC)


async def process_outbox_once(db: AsyncSession, topics: list[str] | None = None) -> int:
    """Process one batch of due outbox messages. Returns handled count.

    Called by the arq loop AND directly by tests (no Redis required).
    Each message is claimed with FOR UPDATE SKIP LOCKED so concurrent
    workers never double-consume.
    """
    load_handlers()
    from sqlalchemy import func as _sql_func

    from app.controlplane.models.outbox import OutboxMessage

    q = (
        select(OutboxMessage)
        .where(
            OutboxMessage.status == "pending",
            # DB-side clock: available_at defaults to the DB's now(), so the
            # due-check must use the same clock — a few ms of app/DB skew
            # otherwise makes freshly enqueued messages invisible (flake).
            OutboxMessage.available_at <= _sql_func.now(),
        )
        .order_by(OutboxMessage.available_at)
        .limit(settings.outbox_batch_size)
        .with_for_update(skip_locked=True)
    )
    if topics:
        q = q.where(OutboxMessage.topic.in_(topics))

    rows = (await db.execute(q)).scalars().all()
    handled = 0
    # R89[12] phase 1 — CLAIM the whole batch in one short transaction:
    # every row flips to processing/locked (or gets its unknown-topic
    # backoff) and the claim commits immediately. This releases the row
    # locks while keeping concurrent pollers out via the status filter, so
    # phase 2 can commit PER MESSAGE without re-exposing the rest of the
    # batch. Previously one commit covered the entire batch under arq's
    # 300s job_timeout — a heavy batch (period close × N tenants) was
    # cancelled, fully rolled back, and retried identically forever.
    claimable = []
    for msg in rows:
        if HANDLERS.get(msg.topic) is None:
            # R98[m15]: unknown topics spun FOREVER with zero log and no
            # attempts increment (a typo'd enqueue was invisible). Log, count
            # the attempt, and dead-letter at the same threshold as failing
            # handlers — a later deploy that knows the topic can requeue via
            # the failed-outbox ops endpoint.
            msg.attempts += 1
            if msg.attempts >= settings.outbox_max_attempts:
                msg.status = "failed"
                msg.last_error = f"no handler registered for topic '{msg.topic}'"
                log.error("outbox_unknown_topic_dead_letter", topic=msg.topic, message_id=msg.id)
            else:
                msg.available_at = _now() + timedelta(minutes=5)
                log.warning(
                    "outbox_unknown_topic",
                    topic=msg.topic,
                    message_id=msg.id,
                    attempts=msg.attempts,
                )
            continue
        msg.status = "processing"
        msg.locked_by = _worker_id()
        msg.locked_at = _now()
        claimable.append(msg)
    await db.commit()

    # Phase 2 — process each claimed message, committing per message so a
    # timeout/crash loses at most the in-flight one (reaper + idempotent
    # handlers cover that window).
    for msg in claimable:
        handler = HANDLERS.get(msg.topic)
        try:
            # Isolate each handler in a SAVEPOINT: a handler that hits a
            # DB-level error (e.g. revenue_share._insert_entry's documented
            # concurrent-loser IntegrityError) would otherwise deactivate the
            # shared batch transaction and poison every SIBLING message in the
            # same poll (PendingRollbackError on the next flush → the whole
            # batch stalls and re-stalls). The nested block rolls back only
            # this message's partial writes; the outer tx stays usable for the
            # status bookkeeping below and for the remaining messages.
            async with db.begin_nested():
                await handler(db, msg.payload)
        except Exception as exc:  # noqa: BLE001 — retry/dead-letter path
            msg.attempts += 1
            msg.last_error = str(exc)[:2000]
            if msg.attempts >= settings.outbox_max_attempts:
                msg.status = "failed"
                log.error("outbox_dead_letter", topic=msg.topic, message_id=msg.id, error=str(exc))
            else:
                msg.status = "pending"
                msg.available_at = _now() + timedelta(seconds=30 * (2**msg.attempts))
                log.warning(
                    "outbox_retry", topic=msg.topic, message_id=msg.id, attempts=msg.attempts
                )
        else:
            msg.status = "done"
            msg.processed_at = _now()
            handled += 1
        msg.locked_by = None
        msg.locked_at = None
        # Per-message commit (phase 1 already released the batch row locks;
        # concurrent pollers skip 'processing' rows via the status filter, so
        # this loop stays the sole writer of each claimed message).
        await db.commit()
    return handled


async def reap_stuck(db: AsyncSession, older_than_minutes: int = 10) -> int:
    """Return crashed-mid-processing messages to pending (lease reaper)."""
    from app.controlplane.models.outbox import OutboxMessage

    # R113[M19]: arq's job-timeout cancellation raises CancelledError — a
    # BaseException the per-message `except Exception` in process_outbox_once
    # never sees, so the in-flight message (and any claimed-but-unstarted
    # siblings) stayed 'processing' until this reaper. The reaper DID return
    # them to pending within one cron cycle, but WITHOUT counting the attempt:
    # a handler that hangs past the timeout on every try retried forever and
    # could never dead-letter. Count the interrupted attempt here and
    # dead-letter at the same threshold as failing handlers. Recovery lives in
    # the reaper (not an in-loop except CancelledError) because a mid-query
    # cancellation leaves the session's connection unusable for bookkeeping.
    # Siblings of a cancelled batch get an attempt overcounted — acceptable:
    # a batch cancelled outbox_max_attempts times over is wedged, not unlucky.
    cutoff = _now() - timedelta(minutes=older_than_minutes)
    dead = await db.execute(
        update(OutboxMessage)
        .where(
            OutboxMessage.status == "processing",
            OutboxMessage.locked_at < cutoff,
            OutboxMessage.attempts >= settings.outbox_max_attempts - 1,
        )
        .values(
            status="failed",
            attempts=OutboxMessage.attempts + 1,
            last_error="lease expired mid-processing (crash or job-timeout cancellation)",
            locked_by=None,
            locked_at=None,
        )
    )
    result = await db.execute(
        update(OutboxMessage)
        .where(
            OutboxMessage.status == "processing",
            OutboxMessage.locked_at < cutoff,
        )
        .values(
            status="pending",
            attempts=OutboxMessage.attempts + 1,
            locked_by=None,
            locked_at=None,
        )
    )
    await db.commit()
    if dead.rowcount:
        log.error("outbox_reap_dead_letter", count=dead.rowcount)
    return result.rowcount + dead.rowcount


# ── arq wiring ───────────────────────────────────────────────


async def _poll_outbox(ctx: dict) -> None:
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await process_outbox_once(db)
        if n:
            log.info("outbox_processed", count=n)


async def _reap_outbox(ctx: dict) -> None:
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await reap_stuck(db)
        if n:
            log.warning("outbox_reaped", count=n)


async def _expire_trials(ctx: dict) -> None:
    from app.controlplane.services.tenants import expire_trials
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await expire_trials(db)
        await db.commit()
        if n:
            log.info("cp_trials_expired", count=n)


async def _sweep_storage(ctx: dict) -> None:
    from app.controlplane.services.metering import sweep_storage
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await sweep_storage(db)
        await db.commit()
        log.info("cp_storage_swept", events=n)


async def _sweep_seats(ctx: dict) -> None:
    from app.controlplane.services.metering import sweep_seats
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await sweep_seats(db)
        await db.commit()
        log.info("cp_seats_swept", events=n)


async def _scan_periods(ctx: dict) -> None:
    from app.controlplane.services.billing import scan_due_periods
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await scan_due_periods(db)
        await db.commit()
        if n:
            log.info("cp_periods_enqueued", count=n)


async def _expire_reservations(ctx: dict) -> None:
    from app.controlplane.services.credits import expire_stale_reservations
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await expire_stale_reservations(db)
        await db.commit()
        if n:
            log.info("cp_reservations_expired", count=n)


async def _sweep_wedged_evals(ctx: dict) -> None:
    # R101[H18]: tasks committed as PROCESSING before the LLM call are wedged
    # forever if the process died mid-call — flip to FAILED + settle holds.
    from app.core.database import AsyncSessionLocal
    from app.services.evaluation import sweep_wedged_evaluations

    async with AsyncSessionLocal() as db:
        n = await sweep_wedged_evaluations(db)
        await db.commit()
        if n:
            log.warning("cp_wedged_evals_swept", count=n)


async def _expire_promos(ctx: dict) -> None:
    from app.controlplane.services.credits import expire_promotional
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await expire_promotional(db)
        await db.commit()
        if n:
            log.info("cp_promos_expired", count=n)


async def _flush_api_counters(ctx: dict) -> None:
    from app.controlplane.services.metering import flush_api_request_counters
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await flush_api_request_counters(db)
        if n:
            log.info("cp_api_counters_flushed", events=n)


async def _sweep_workflow_runtime(ctx: dict) -> None:
    """R66[2]: sweep_stale is the ONLY code that expires overdue reviews and
    recovers stalled runs, but it ran only lazily (on run detail reads) and
    via a manual admin endpoint. An unviewed WAITING_REVIEW run's due_at
    never fired autonomously — 'timeout' semantics that require someone to
    look at the run are not timeouts. Run it on a schedule."""
    from app.core.database import AsyncSessionLocal
    from app.services.workflow_runtime import dispatch_advance, sweep_stale

    async with AsyncSessionLocal() as db:
        stats = await sweep_stale(db)
        await db.commit()
    # sweep only repairs step state; each touched run must be re-advanced.
    for run_id in stats.get("run_ids", []):
        dispatch_advance(run_id)
    if stats.get("expired_leases") or stats.get("expired_reviews") or stats.get("stalled_runs"):
        log.info(
            "cp_workflow_sweep",
            expired_leases=stats.get("expired_leases", 0),
            expired_reviews=stats.get("expired_reviews", 0),
            stalled_runs=stats.get("stalled_runs", 0),
        )


def _cron_jobs() -> list:
    """Cron registry — later phases append their sweeps here."""
    from arq.cron import cron

    return [
        # Outbox poll every 15s (arq cron supports second-level sets).
        cron(_poll_outbox, second={0, 15, 30, 45}, name="cp_outbox_poll"),
        cron(_reap_outbox, minute=set(range(0, 60, 10)), second=5, name="cp_outbox_reaper"),
        # Trial expiry: hourly at :12 (off-minute by design)
        cron(_expire_trials, minute=12, name="cp_trial_expiry"),
        # P3 sweeps: storage daily 03:23; seats monthly (1st, 04:17);
        # api-counter flush hourly at :05
        cron(_sweep_storage, hour=3, minute=23, name="cp_storage_sweep"),
        cron(_sweep_seats, day={1}, hour=4, minute=17, name="cp_seat_sweep"),
        cron(_flush_api_counters, minute=5, name="cp_api_flush"),
        # P5 sweeps: reservation expiry every 30 min; promo expiry daily 02:37
        cron(_expire_reservations, minute={7, 37}, name="cp_reservation_expiry"),
        cron(_sweep_wedged_evals, minute={13, 43}, name="cp_wedged_eval_sweep"),
        cron(_expire_promos, hour=2, minute=37, name="cp_promo_expiry"),
        # P6: billing period close scan hourly at :47
        cron(_scan_periods, minute=47, name="cp_period_scan"),
        # R66[2]: workflow sweeper (review due_at expiry + stalled-run
        # recovery) every 5 minutes — off-minute by design.
        cron(_sweep_workflow_runtime, minute=set(range(3, 60, 5)), name="cp_workflow_sweep"),
        # P10: tls refresh
    ]


def _redis_settings():
    from arq.connections import RedisSettings

    return RedisSettings.from_dsn(settings.redis_url)


class WorkerSettings:
    """arq worker settings: outbox poll loop + cron jobs."""

    redis_settings = _redis_settings()

    @staticmethod
    async def on_startup(ctx: dict) -> None:
        from app.core.logging import setup_logging

        setup_logging(level=settings.log_level, fmt=settings.log_format)
        log.info("cp_worker_started")

    @staticmethod
    async def on_shutdown(ctx: dict) -> None:
        # R89[M15]: the sweep cron spawns fire-and-forget advance_run tasks
        # (dispatch_advance) that arq's shutdown does NOT wait for — a worker
        # restart cancelled them mid-provider-call, leaving RUNNING steps for
        # the sweeper to recover a full cron cycle later. Drain like the API
        # lifespan does.
        from app.services.workflow_runtime import drain_workflow_tasks

        await drain_workflow_tasks(timeout=30.0)
        log.info("cp_worker_stopped")

    functions = [_poll_outbox]
    cron_jobs = _cron_jobs()
