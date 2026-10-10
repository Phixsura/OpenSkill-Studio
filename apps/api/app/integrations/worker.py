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
