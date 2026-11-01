"""App API Developer Platform API Deprecation Schedule — plan and track API deprecations."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeprecationSchedule:
    endpoint: str
    version: str
    deprecated_at: str  # ISO date
    sunset_at: str  # ISO date
    replacement: str = ""
    active_consumers: int = 0
    migration_pct: float = 0.0

    @property
    def fully_migrated(self) -> bool:
        return self.migration_pct >= 100.0

    @property
    def urgency(self) -> str:
        if self.active_consumers == 0: return "done"
        if self.migration_pct < 50: return "critical"
        if self.migration_pct < 80: return "high"
        if self.migration_pct < 95: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeprecationSchedule:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str, str], DeprecationSchedule] = {}

    def schedule(self, installation_id: str, endpoint: str, version: str, deprecated_at: str, sunset_at: str, replacement: str = "") -> DeprecationSchedule:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, version, endpoint)
        s = DeprecationSchedule(endpoint=endpoint, version=version, deprecated_at=deprecated_at, sunset_at=sunset_at, replacement=replacement)
        self._schedules[key] = s
        return s

    def update_migration(self, installation_id: str, endpoint: str, version: str, active_consumers: int, migration_pct: float) -> DeprecationSchedule:
        key = (installation_id, version, endpoint)
        s = self._schedules.get(key)
        if s is None: raise KeyError(f"No schedule for {endpoint} {version}")
        s.active_consumers = active_consumers
        s.migration_pct = migration_pct
        return s

    def critical_deprecations(self, installation_id: str) -> list[DeprecationSchedule]:
        return [s for (inst, _, _), s in self._schedules.items() if inst == installation_id and s.urgency in ("critical", "high")]

    def all_schedules(self, installation_id: str) -> list[DeprecationSchedule]:
        return [s for (inst, _, _), s in self._schedules.items() if inst == installation_id]
