"""Ecosystem facade — the ONLY entry point for product code (ADR-016 §6).

Product code (registry, matching, workforce, workflow runtime) imports ONLY
from this module. Only approved intelligence (lifecycle verified|recommended,
human-verified observations, completed benchmarks) crosses this boundary —
raw unverified observations never leak into production behavior.
"""

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession


async def get_registry_badges(
    db: AsyncSession, entity_refs: list[tuple[str, str]]
) -> dict:
    """Evidence-backed registry badges: benchmark_verified, production_verified,
    dependency_update_available, provider_sunset_risk."""
    from app.ecosystem.services.signals import SignalsService

    return await SignalsService(db).registry_badges(entity_refs=entity_refs)


async def get_matching_signals(
    db: AsyncSession, *, capability_key: str | None = None
) -> list[dict]:
    """Approved-only soft signals for the matching engine (Part N)."""
    from app.ecosystem.services.signals import SignalsService

    return await SignalsService(db).matching_signals(capability_key=capability_key)


async def get_workforce_signals(db: AsyncSession) -> list[dict]:
    """Emerging/obsolete capability planning signals (Part O). Advisory only."""
    from app.ecosystem.services.signals import SignalsService

    return await SignalsService(db).workforce_signals()


async def record_production_telemetry(
    db: AsyncSession,
    *,
    window_start: datetime,
    window_end: datetime,
) -> int:
    """Aggregate workflow-run telemetry into privacy-safe snapshots (Part G)."""
    from app.ecosystem.services.telemetry import TelemetryService

    snapshots = await TelemetryService(db).aggregate_workflow_runs(
        window_start=window_start, window_end=window_end
    )
    return len(snapshots)
