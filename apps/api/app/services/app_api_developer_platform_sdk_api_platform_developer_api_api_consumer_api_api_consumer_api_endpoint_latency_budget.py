"""API Consumer Endpoint Latency Budget — per-consumer latency budgets."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class LatencyBudget:
    consumer_id: str
    endpoint: str
    method: str
    budget_ms: int
    total_requests: int = 0
    within_budget: int = 0

    @property
    def compliance_pct(self) -> float:
        if self.total_requests == 0: return 100.0
        return round((self.within_budget / self.total_requests) * 100, 1)

    @property
    def meeting(self) -> bool:
        return self.compliance_pct >= 95.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointLatencyBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str, str, str], LatencyBudget] = {}

    def set_budget(self, installation_id: str, consumer_id: str, endpoint: str, method: str, budget_ms: int) -> LatencyBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if budget_ms < 1: raise ValueError("budget_ms must be >= 1")
        b = LatencyBudget(consumer_id=consumer_id, endpoint=endpoint, method=method.upper(), budget_ms=budget_ms)
        self._budgets[(installation_id, consumer_id, method.upper(), endpoint)] = b
        return b

    def record(self, installation_id: str, consumer_id: str, endpoint: str, method: str, latency_ms: float) -> LatencyBudget:
        key = (installation_id, consumer_id, method.upper(), endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {consumer_id}/{method}/{endpoint}")
        b.total_requests += 1
        if latency_ms <= b.budget_ms: b.within_budget += 1
        return b

    def violations(self, installation_id: str, consumer_id: str | None = None) -> list[LatencyBudget]:
        budgets = [b for (inst, cid, _, _), b in self._budgets.items() if inst == installation_id and (consumer_id is None or cid == consumer_id)]
        return [b for b in budgets if not b.meeting and b.total_requests > 0]

    def list_budgets(self, installation_id: str) -> list[LatencyBudget]:
        return [b for (inst, _, _, _), b in self._budgets.items() if inst == installation_id]
