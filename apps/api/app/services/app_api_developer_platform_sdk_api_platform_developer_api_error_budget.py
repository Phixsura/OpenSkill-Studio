"""API Error Budget — track SLO error budgets and burn rates."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBudget:
    endpoint: str
    slo_target_pct: float  # e.g. 99.9
    window_requests: int = 0
    error_count: int = 0

    @property
    def budget_total(self) -> float:
        return self.window_requests * (1 - self.slo_target_pct / 100)

    @property
    def budget_remaining(self) -> float:
        return max(0.0, self.budget_total - self.error_count)

    @property
    def budget_consumed_pct(self) -> float:
        total = self.budget_total
        if total <= 0: return 0.0
        return round(min(100.0, (self.error_count / total) * 100), 1)

    @property
    def burn_rate(self) -> float:
        """How fast budget is being consumed (1.0 = normal, >1 = faster)."""
        total = self.budget_total
        if total <= 0 or self.window_requests <= 0: return 0.0
        expected_errors = total * (self.error_count / max(1, self.window_requests)) * self.window_requests / max(1, total)
        return round(self.error_count / max(1, total), 2)

    @property
    def status(self) -> str:
        pct = self.budget_consumed_pct
        if pct >= 100: return "exhausted"
        if pct >= 80: return "critical"
        if pct >= 50: return "warning"
        return "healthy"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiErrorBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ErrorBudget] = {}

    def create(self, installation_id: str, endpoint: str, slo_target_pct: float) -> ErrorBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= slo_target_pct <= 100: raise ValueError("SLO target must be 90-100%")
        key = (installation_id, endpoint)
        b = ErrorBudget(endpoint=endpoint, slo_target_pct=slo_target_pct)
        self._budgets[key] = b
        return b

    def record_requests(self, installation_id: str, endpoint: str, total: int, errors: int) -> ErrorBudget:
        key = (installation_id, endpoint)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {endpoint}")
        if errors < 0 or total < 0: raise ValueError("Counts must be non-negative")
        if errors > total: raise ValueError("Errors cannot exceed total")
        b.window_requests += total
        b.error_count += errors
        return b

    def get_budget(self, installation_id: str, endpoint: str) -> ErrorBudget:
        b = self._budgets.get((installation_id, endpoint))
        if b is None: raise KeyError(f"No budget for {endpoint}")
        return b

    def alerts(self, installation_id: str, threshold_pct: float = 80.0) -> list[ErrorBudget]:
        return [b for (inst, _), b in self._budgets.items()
                if inst == installation_id and b.budget_consumed_pct >= threshold_pct]

    def list_budgets(self, installation_id: str) -> list[ErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
