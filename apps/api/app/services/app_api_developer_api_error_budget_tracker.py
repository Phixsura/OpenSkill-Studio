"""App API Developer Error Budget Tracker — SLO-based error budget management."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBudget:
    endpoint: str
    slo_target_pct: float  # e.g. 99.9
    total_requests: int = 0
    failed_requests: int = 0

    @property
    def current_success_pct(self) -> float:
        if self.total_requests == 0: return 100.0
        return round((self.total_requests - self.failed_requests) / self.total_requests * 100, 3)

    @property
    def budget_remaining_pct(self) -> float:
        allowed_failure_pct = 100.0 - self.slo_target_pct
        actual_failure_pct = (self.failed_requests / self.total_requests * 100) if self.total_requests > 0 else 0.0
        remaining = allowed_failure_pct - actual_failure_pct
        return round(max(0.0, remaining), 3)

    @property
    def budget_exhausted(self) -> bool:
        return self.budget_remaining_pct <= 0.0

class AppAPIDeveloperAPIErrorBudgetTracker:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ErrorBudget] = {}

    def create(self, installation_id: str, endpoint: str, slo_target_pct: float) -> ErrorBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if not 0 < slo_target_pct <= 100: raise ValueError("slo_target_pct must be between 0 and 100")
        key = (installation_id, endpoint)
        b = ErrorBudget(endpoint=endpoint, slo_target_pct=slo_target_pct)
        self._budgets[key] = b
        return b

    def record(self, installation_id: str, endpoint: str, success: bool) -> ErrorBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {endpoint}")
        b.total_requests += 1
        if not success: b.failed_requests += 1
        return b

    def get(self, installation_id: str, endpoint: str) -> ErrorBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {endpoint}")
        return b

    def exhausted(self, installation_id: str) -> list[ErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and b.budget_exhausted]
