"""Integration fabric worker handlers (ADR-018 §3/§12).

Rides the controlplane transactional-outbox worker: handlers register on the
shared topic registry and MUST be idempotent. Tests drive them inline via
app.controlplane.worker.process_outbox_once(db).
"""

from __future__ import annotations

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.controlplane.worker import register_handler
from app.integrations.services import events as events_svc

log = structlog.get_logger()


@register_handler(events_svc.TOPIC_EVENT_CREATED)
async def _on_event_created(db: AsyncSession, payload: dict) -> None:
    await events_svc.handle_event_created(db, payload)


@register_handler(events_svc.TOPIC_DELIVERY_ATTEMPT)
async def _on_delivery_attempt(db: AsyncSession, payload: dict) -> None:
    await events_svc.handle_delivery_attempt(db, payload)


@register_handler("intg.sync.run")
async def _on_sync_run(db: AsyncSession, payload: dict) -> None:
    """Sync runs manage their OWN transactions (per-batch cursor commits —
    ADR-018 §11.3), which is incompatible with the outbox handler SAVEPOINT.
    Drive the run on a dedicated session; the handler itself stays cheap and
    idempotent (execute_run's atomic claim makes redelivery a no-op)."""
    from app.core.database import AsyncSessionLocal
    from app.integrations.services.sync_engine import execute_run

    run_id = payload.get("run_id", "")
    async with AsyncSessionLocal() as own_session:
        await execute_run(own_session, run_id)
