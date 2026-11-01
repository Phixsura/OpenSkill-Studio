"""API Endpoint Deprecation Scheduler — schedule and track endpoint deprecations."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class DeprecationPhase(str, Enum):
    ANNOUNCED = "announced"
    WARNING = "warning"
    SUNSET = "sunset"
    REMOVED = "removed"

@dataclass
class DeprecationSchedule:
    endpoint: str
    method: str
    phase: DeprecationPhase = DeprecationPhase.ANNOUNCED
    replacement: str = ""
    announced_at: float = field(default_factory=time.time)
    sunset_at: float = 0.0  # unix ts when endpoint will be removed
    active_consumers: int = 0
    migration_guide_url: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiEndpointDeprecationScheduler:
    def __init__(self) -> None:
        self._schedules: dict[tuple[str, str, str], DeprecationSchedule] = {}

    def schedule(self, installation_id: str, endpoint: str, method: str, sunset_at: float, replacement: str = "", migration_guide_url: str = "") -> DeprecationSchedule:
        if not installation_id: raise ValueError("installation_id is required")
        if sunset_at <= time.time(): raise ValueError("sunset_at must be in the future")
        key = (installation_id, method.upper(), endpoint)
        if key in self._schedules: raise ValueError(f"Deprecation for {method} {endpoint} already scheduled")
        ds = DeprecationSchedule(endpoint=endpoint, method=method.upper(), replacement=replacement, sunset_at=sunset_at, migration_guide_url=migration_guide_url)
        self._schedules[key] = ds
        return ds

    def advance_phase(self, installation_id: str, endpoint: str, method: str, phase: DeprecationPhase) -> DeprecationSchedule:
        ds = self._get(installation_id, endpoint, method)
        phase_order = list(DeprecationPhase)
        current_idx = phase_order.index(ds.phase)
        new_idx = phase_order.index(phase)
        if new_idx <= current_idx: raise ValueError(f"Cannot move from {ds.phase.value} to {phase.value}")
        ds.phase = phase
        return ds

    def update_consumers(self, installation_id: str, endpoint: str, method: str, count: int) -> DeprecationSchedule:
        ds = self._get(installation_id, endpoint, method)
        if count < 0: raise ValueError("Consumer count must be non-negative")
        ds.active_consumers = count
        return ds

    def overdue(self, installation_id: str) -> list[DeprecationSchedule]:
        now = time.time()
        return [ds for (inst, _, _), ds in self._schedules.items()
                if inst == installation_id and ds.sunset_at <= now and ds.phase != DeprecationPhase.REMOVED]

    def list_schedules(self, installation_id: str) -> list[DeprecationSchedule]:
        return [ds for (inst, _, _), ds in self._schedules.items() if inst == installation_id]

    def _get(self, installation_id: str, endpoint: str, method: str) -> DeprecationSchedule:
        ds = self._schedules.get((installation_id, method.upper(), endpoint))
        if ds is None: raise KeyError(f"No deprecation for {method} {endpoint}")
        return ds
