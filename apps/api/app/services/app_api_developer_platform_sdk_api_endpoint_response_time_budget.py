"""App API Developer Endpoint Response Time Budget — enforce response time targets."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ResponseTimeBudget:
    endpoint: str
    budget_ms: float
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    checks: int = 0
    violations: int = 0

    @property
    def within_budget(self) -> bool:
        return self.p99_ms <= self.budget_ms

    @property
    def violation_rate(self) -> float:
        return round(self.violations / self.checks * 100, 1) if self.checks > 0 else 0.0

    @property
    def headroom_pct(self) -> float:
        if self.budget_ms == 0: return 0.0
        return round((self.budget_ms - self.p99_ms) / self.budget_ms * 100, 1)

class AppAPIDeveloperPlatformSDKApiEndpointResponseTimeBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ResponseTimeBudget] = {}

    def set_budget(self, installation_id: str, endpoint: str, budget_ms: float) -> ResponseTimeBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if budget_ms <= 0: raise ValueError("budget must be positive")
        key = (installation_id, endpoint)
        b = ResponseTimeBudget(endpoint=endpoint, budget_ms=budget_ms)
        self._budgets[key] = b
        return b

    def check(self, installation_id: str, endpoint: str, p50: float, p95: float, p99: float) -> ResponseTimeBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {endpoint}")
        b.p50_ms = p50
        b.p95_ms = p95
        b.p99_ms = p99
        b.checks += 1
        if not b.within_budget: b.violations += 1
        return b

    def over_budget(self, installation_id: str) -> list[ResponseTimeBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and not b.within_budget]

    def all_budgets(self, installation_id: str) -> list[ResponseTimeBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
