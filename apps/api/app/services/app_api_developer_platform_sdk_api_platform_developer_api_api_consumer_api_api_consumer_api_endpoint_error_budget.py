"""API Consumer Endpoint Error Budget — per-consumer per-endpoint error budgets."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerEndpointBudget:
    consumer_id: str
    endpoint: str
    method: str
    slo_pct: float = 99.5
    total_requests: int = 0
    error_count: int = 0

    @property
    def budget_total(self) -> float:
        return self.total_requests * (1 - self.slo_pct / 100)

    @property
    def budget_used_pct(self) -> float:
        bt = self.budget_total
        if bt <= 0: return 0.0
        return round(min(100.0, (self.error_count / bt) * 100), 1)

    @property
    def status(self) -> str:
        p = self.budget_used_pct
        if p >= 100: return "exhausted"
        if p >= 80: return "critical"
        if p >= 50: return "warning"
        return "healthy"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointErrorBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str, str, str], ConsumerEndpointBudget] = {}

    def create(self, installation_id: str, consumer_id: str, endpoint: str, method: str, slo_pct: float = 99.5) -> ConsumerEndpointBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= slo_pct <= 100: raise ValueError("SLO must be 90-100%")
        b = ConsumerEndpointBudget(consumer_id=consumer_id, endpoint=endpoint, method=method.upper(), slo_pct=slo_pct)
        self._budgets[(installation_id, consumer_id, method.upper(), endpoint)] = b
        return b

    def record(self, installation_id: str, consumer_id: str, endpoint: str, method: str, error: bool) -> ConsumerEndpointBudget:
        key = (installation_id, consumer_id, method.upper(), endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {consumer_id}/{method}/{endpoint}")
        b.total_requests += 1
        if error: b.error_count += 1
        return b

    def at_risk(self, installation_id: str, consumer_id: str | None = None) -> list[ConsumerEndpointBudget]:
        budgets = [b for (inst, cid, _, _), b in self._budgets.items() if inst == installation_id and (consumer_id is None or cid == consumer_id)]
        return [b for b in budgets if b.budget_used_pct >= 80]

    def list_budgets(self, installation_id: str) -> list[ConsumerEndpointBudget]:
        return [b for (inst, _, _, _), b in self._budgets.items() if inst == installation_id]
