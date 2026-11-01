"""App API Developer API Performance Budget — enforce latency/size budgets."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PerformanceBudget:
    endpoint: str
    max_latency_ms: float
    max_response_bytes: int
    actual_latency_ms: float = 0.0
    actual_response_bytes: int = 0
    check_count: int = 0
    violation_count: int = 0

    @property
    def latency_ok(self) -> bool:
        return self.actual_latency_ms <= self.max_latency_ms

    @property
    def size_ok(self) -> bool:
        return self.actual_response_bytes <= self.max_response_bytes

    @property
    def within_budget(self) -> bool:
        return self.latency_ok and self.size_ok

class AppAPIDeveloperAPIApiPerformanceBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], PerformanceBudget] = {}

    def set_budget(self, installation_id: str, endpoint: str, max_latency_ms: float, max_response_bytes: int) -> PerformanceBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if max_latency_ms <= 0: raise ValueError("max_latency must be positive")
        if max_response_bytes <= 0: raise ValueError("max_response_bytes must be positive")
        b = PerformanceBudget(endpoint=endpoint, max_latency_ms=max_latency_ms, max_response_bytes=max_response_bytes)
        self._budgets[(installation_id, endpoint)] = b
        return b

    def check(self, installation_id: str, endpoint: str, latency_ms: float, response_bytes: int) -> PerformanceBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {endpoint}")
        b.actual_latency_ms = latency_ms
        b.actual_response_bytes = response_bytes
        b.check_count += 1
        if not b.within_budget: b.violation_count += 1
        return b

    def violations(self, installation_id: str) -> list[PerformanceBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and not b.within_budget]

    def all_budgets(self, installation_id: str) -> list[PerformanceBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
