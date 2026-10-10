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
