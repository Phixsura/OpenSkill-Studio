"""App API Developer Platform Usage Breakdown — break down usage across all dimensions."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class UsageBreakdown:
    period: str
    api_calls: int = 0
    webhook_deliveries: int = 0
    storage_mb: float = 0.0
    compute_hours: float = 0.0
    bandwidth_gb: float = 0.0
    active_consumers: int = 0
    active_keys: int = 0

    @property
    def total_operations(self) -> int:
        return self.api_calls + self.webhook_deliveries

    @property
    def cost_weighted_score(self) -> float:
        return round(self.api_calls * 0.001 + self.webhook_deliveries * 0.002 + self.storage_mb * 0.01 + self.compute_hours * 0.1 + self.bandwidth_gb * 0.05, 2)

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformUsageBreakdown:
    def __init__(self) -> None:
        self._breakdowns: dict[tuple[str, str], UsageBreakdown] = {}

    def record(self, installation_id: str, period: str, **kwargs) -> UsageBreakdown:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, period)
        b = UsageBreakdown(period=period)
        for k, v in kwargs.items():
            if hasattr(b, k): setattr(b, k, v)
        self._breakdowns[key] = b
        return b

    def get(self, installation_id: str, period: str) -> UsageBreakdown | None:
        return self._breakdowns.get((installation_id, period))

    def trend(self, installation_id: str) -> list[UsageBreakdown]:
        breakdowns = [b for (inst, _), b in self._breakdowns.items() if inst == installation_id]
        return sorted(breakdowns, key=lambda b: b.period)

    def total_operations(self, installation_id: str) -> int:
        return sum(b.total_operations for (inst, _), b in self._breakdowns.items() if inst == installation_id)
