"""API Consumer Error Budget Tracker — track SLO error budget consumption over time."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ErrorBudgetWindow:
    consumer_id: str
    slo_target_pct: float = 99.9
    window_requests: int = 0
    window_errors: int = 0

    @property
    def budget_total(self) -> float:
        return self.window_requests * (1 - self.slo_target_pct / 100)

    @property
    def budget_consumed(self) -> float:
        total = self.budget_total
        if total <= 0: return 0.0
        return round(min(100.0, (self.window_errors / total) * 100), 1)

    @property
    def budget_remaining_pct(self) -> float:
        return round(max(0.0, 100.0 - self.budget_consumed), 1)

    @property
    def status(self) -> str:
        c = self.budget_consumed
        if c >= 100: return "exhausted"
        if c >= 80: return "critical"
        if c >= 50: return "warning"
        return "healthy"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiErrorBudgetTracker:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ErrorBudgetWindow] = {}

    def create(self, installation_id: str, consumer_id: str, slo_target_pct: float = 99.9) -> ErrorBudgetWindow:
        if not installation_id: raise ValueError("installation_id is required")
        if not 90 <= slo_target_pct <= 100: raise ValueError("SLO must be 90-100%")
        b = ErrorBudgetWindow(consumer_id=consumer_id, slo_target_pct=slo_target_pct)
        self._budgets[(installation_id, consumer_id)] = b
        return b

    def record(self, installation_id: str, consumer_id: str, requests: int, errors: int) -> ErrorBudgetWindow:
        b = self._budgets.get((installation_id, consumer_id))
        if b is None: raise KeyError(f"No budget for {consumer_id}")
        if errors > requests: raise ValueError("Errors cannot exceed requests")
        b.window_requests += requests
        b.window_errors += errors
        return b

    def at_risk(self, installation_id: str, threshold_pct: float = 80.0) -> list[ErrorBudgetWindow]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and b.budget_consumed >= threshold_pct]

    def list_budgets(self, installation_id: str) -> list[ErrorBudgetWindow]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
