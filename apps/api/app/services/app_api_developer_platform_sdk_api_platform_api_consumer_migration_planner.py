"""App API Developer Consumer Migration Planner — plan consumer API version migrations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class MigrationPlan:
    consumer_id: str
    from_version: str
    to_version: str
    breaking_changes: int = 0
    estimated_effort_hours: float = 0.0
    status: str = "planned"  # "planned", "in_progress", "completed", "blocked"
    blockers: list[str] = field(default_factory=list)

    @property
    def complexity(self) -> str:
        if self.breaking_changes >= 10 or self.estimated_effort_hours >= 40: return "high"
        if self.breaking_changes >= 3 or self.estimated_effort_hours >= 8: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiPlatformApiConsumerMigrationPlanner:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], MigrationPlan] = {}

    def plan(self, installation_id: str, consumer_id: str, from_version: str, to_version: str, breaking_changes: int = 0, estimated_effort_hours: float = 0.0) -> MigrationPlan:
        if not installation_id: raise ValueError("installation_id is required")
        if from_version == to_version: raise ValueError("versions must differ")
        key = (installation_id, consumer_id)
        p = MigrationPlan(consumer_id=consumer_id, from_version=from_version, to_version=to_version, breaking_changes=breaking_changes, estimated_effort_hours=estimated_effort_hours)
        self._plans[key] = p
        return p

    def update_status(self, installation_id: str, consumer_id: str, status: str) -> MigrationPlan:
        key = (installation_id, consumer_id)
        p = self._plans.get(key)
        if p is None: raise KeyError(f"No plan for {consumer_id}")
        if status not in ("planned", "in_progress", "completed", "blocked"): raise ValueError("invalid status")
        p.status = status
        return p

    def blocked_plans(self, installation_id: str) -> list[MigrationPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id and p.status == "blocked"]

    def pending_plans(self, installation_id: str) -> list[MigrationPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id and p.status in ("planned", "in_progress")]

    def all_plans(self, installation_id: str) -> list[MigrationPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id]
