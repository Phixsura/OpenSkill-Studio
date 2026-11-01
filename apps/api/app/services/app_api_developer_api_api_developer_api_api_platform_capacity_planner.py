"""App API Developer Platform Capacity Planner — forecast and plan platform capacity."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class CapacityPlan:
    resource: str  # "api_capacity", "webhook_throughput", "storage", "compute"
    current_usage: float
    max_capacity: float
    growth_rate_pct: float  # monthly
    unit: str = ""

    @property
    def utilization_pct(self) -> float:
        return round(self.current_usage / self.max_capacity * 100, 1) if self.max_capacity > 0 else 0.0

    @property
    def months_until_full(self) -> float:
        if self.growth_rate_pct <= 0 or self.current_usage >= self.max_capacity: return 0.0
        remaining = self.max_capacity - self.current_usage
        monthly_growth = self.current_usage * self.growth_rate_pct / 100
        if monthly_growth <= 0: return float("inf")
        return round(remaining / monthly_growth, 1)

    @property
    def needs_scaling(self) -> bool:
        return self.utilization_pct >= 75 or self.months_until_full <= 3

class AppAPIDeveloperAPIApiDeveloperApiApiPlatformCapacityPlanner:
    def __init__(self) -> None:
        self._plans: dict[tuple[str, str], CapacityPlan] = {}

    def plan(self, installation_id: str, resource: str, current_usage: float, max_capacity: float, growth_rate_pct: float, unit: str = "") -> CapacityPlan:
        if not installation_id: raise ValueError("installation_id is required")
        if max_capacity <= 0: raise ValueError("max_capacity must be positive")
        key = (installation_id, resource)
        p = CapacityPlan(resource=resource, current_usage=current_usage, max_capacity=max_capacity, growth_rate_pct=growth_rate_pct, unit=unit)
        self._plans[key] = p
        return p

    def needs_scaling(self, installation_id: str) -> list[CapacityPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id and p.needs_scaling]

    def all_plans(self, installation_id: str) -> list[CapacityPlan]:
        return [p for (inst, _), p in self._plans.items() if inst == installation_id]
