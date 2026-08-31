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
    import app.controlplane.services.rating  # noqa: F401
    import app.controlplane.services.settlement_handlers  # noqa: F401
    # P6: billing (period.close_due); P7: revenue share (invoice.finalized,
    # purchase.paid); P10: provisioning (provision.run) — appended as phases land.


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
    for msg in rows:
        handler = HANDLERS.get(msg.topic)
        if handler is None:
            # Unknown topic — a later deploy may know it; back off, don't burn attempts
            msg.available_at = _now() + timedelta(minutes=5)
            continue
        msg.status = "processing"
        msg.locked_by = _worker_id()
        msg.locked_at = _now()
        await db.flush()
        try:
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
    await db.commit()
    return handled


async def reap_stuck(db: AsyncSession, older_than_minutes: int = 10) -> int:
    """Return crashed-mid-processing messages to pending (lease reaper)."""
    from app.controlplane.models.outbox import OutboxMessage

    result = await db.execute(
        update(OutboxMessage)
        .where(
            OutboxMessage.status == "processing",
            OutboxMessage.locked_at < _now() - timedelta(minutes=older_than_minutes),
        )
        .values(status="pending", locked_by=None, locked_at=None)
    )
    await db.commit()
    return result.rowcount


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


async def _expire_reservations(ctx: dict) -> None:
    from app.controlplane.services.credits import expire_stale_reservations
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as db:
        n = await expire_stale_reservations(db)
        await db.commit()
        if n:
            log.info("cp_reservations_expired", count=n)


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
        cron(_expire_promos, hour=2, minute=37, name="cp_promo_expiry"),
        # P6: period close scan
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
        log.info("cp_worker_stopped")

    functions = [_poll_outbox]
    cron_jobs = _cron_jobs()
