"""API Endpoint Response Time Budget — allocate time budgets per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class TimeBudget:
    endpoint: str
    method: str
    budget_ms: int
    total_requests: int = 0
    within_budget: int = 0
    over_budget: int = 0

    @property
    def compliance_pct(self) -> float:
        if self.total_requests == 0: return 100.0
        return round((self.within_budget / self.total_requests) * 100, 1)

    @property
    def meeting_budget(self) -> bool:
        return self.compliance_pct >= 95.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEndpointResponseTimeBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str, str], TimeBudget] = {}

    def set_budget(self, installation_id: str, endpoint: str, method: str, budget_ms: int) -> TimeBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if budget_ms < 1: raise ValueError("budget_ms must be >= 1")
        b = TimeBudget(endpoint=endpoint, method=method.upper(), budget_ms=budget_ms)
        self._budgets[(installation_id, method.upper(), endpoint)] = b
        return b

    def record(self, installation_id: str, endpoint: str, method: str, latency_ms: float) -> TimeBudget:
        key = (installation_id, method.upper(), endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {method} {endpoint}")
        b.total_requests += 1
        if latency_ms <= b.budget_ms: b.within_budget += 1
        else: b.over_budget += 1
        return b

    def violations(self, installation_id: str) -> list[TimeBudget]:
        return [b for (inst, _, _), b in self._budgets.items() if inst == installation_id and not b.meeting_budget]

    def list_budgets(self, installation_id: str) -> list[TimeBudget]:
        return [b for (inst, _, _), b in self._budgets.items() if inst == installation_id]
