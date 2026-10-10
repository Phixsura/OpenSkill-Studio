"""Integration fabric facade (ADR-018 §3).

The ONLY surface other packages may import from app.integrations.
Kept deliberately thin in P1; the event-mesh emit API lands in P2.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession


async def sync_provider_catalog(db: AsyncSession) -> int:
    """Upsert the in-repo provider catalog (idempotent; startup/admin use)."""
    from app.integrations.services.connections import ConnectionService

    return await ConnectionService(db).sync_provider_catalog()


async def emit_event(
    db: AsyncSession,
    org_id: str,
    event_type: str,
    *,
    subject: str | None = None,
    data: dict | None = None,
    version: int = 1,
):
    """Append a canonical mesh event (CloudEvents) + its outbox message in
    the CALLER's transaction (ADR-018 §12.1). ``event_type`` is the bare
    catalog name, e.g. "project.approved" → com.openskill.project.approved.v1.
    Delivery fan-out happens asynchronously in the outbox worker."""
    from app.integrations.services.events import emit_event as _emit

    return await _emit(db, org_id, event_type, subject=subject, data=data, version=version)
