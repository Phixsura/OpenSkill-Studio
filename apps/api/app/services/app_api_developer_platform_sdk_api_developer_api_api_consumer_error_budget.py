"""App API Developer Consumer Error Budget — per-consumer SLO error budget tracking."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerErrorBudget:
    consumer_id: str
    slo_pct: float
    total_requests: int = 0
    failed_requests: int = 0

    @property
    def current_success_pct(self) -> float:
        if self.total_requests == 0: return 100.0
        return round((self.total_requests - self.failed_requests) / self.total_requests * 100, 3)

    @property
    def budget_remaining_pct(self) -> float:
        allowed = 100.0 - self.slo_pct
        actual = (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
        return round(max(0, allowed - actual), 3)

    @property
    def exhausted(self) -> bool:
        return self.budget_remaining_pct <= 0 and self.total_requests > 0

    @property
    def burn_rate(self) -> float:
        allowed = 100.0 - self.slo_pct
        actual = (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
        return round(actual / allowed, 2) if allowed > 0 else 0.0

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiConsumerErrorBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ConsumerErrorBudget] = {}

    def create(self, installation_id: str, consumer_id: str, slo_pct: float) -> ConsumerErrorBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= slo_pct <= 100: raise ValueError("slo must be 90-100")
        key = (installation_id, consumer_id)
        b = ConsumerErrorBudget(consumer_id=consumer_id, slo_pct=slo_pct)
        self._budgets[key] = b
        return b

    def record(self, installation_id: str, consumer_id: str, success: bool) -> ConsumerErrorBudget:
        key = (installation_id, consumer_id)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {consumer_id}")
        b.total_requests += 1
        if not success: b.failed_requests += 1
        return b

    def exhausted_consumers(self, installation_id: str) -> list[ConsumerErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and b.exhausted]

    def high_burn_rate(self, installation_id: str, threshold: float = 1.0) -> list[ConsumerErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and b.burn_rate >= threshold]

    def all_budgets(self, installation_id: str) -> list[ConsumerErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
