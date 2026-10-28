"""App Error Budget — track SLO-based error budgets.

Manages error budgets:
- Define SLO targets per service
- Consume budget on errors
- Calculate remaining budget and burn rate
- Alert when budget is exhausted
- Per-installation scoped budgets
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class ErrorBudget:
    """An error budget for a service."""

    service_id: str
    slo_target: float  # e.g., 99.9 (%)
    window_requests: int  # total requests in window
    error_count: int = 0

    @property
    def budget_total(self) -> int:
        """Max errors allowed in window."""
        return int(self.window_requests * (1 - self.slo_target / 100))

    @property
    def budget_remaining(self) -> int:
        return max(0, self.budget_total - self.error_count)

    @property
    def budget_consumed_pct(self) -> float:
        if self.budget_total == 0:
            return 100.0 if self.error_count > 0 else 0.0
        return round(self.error_count / self.budget_total * 100, 1)

    @property
    def is_exhausted(self) -> bool:
        return self.error_count >= self.budget_total

    @property
    def current_error_rate(self) -> float:
        if self.window_requests == 0:
            return 0.0
        return round(self.error_count / self.window_requests * 100, 3)


class AppErrorBudget:
    """Track SLO-based error budgets."""

    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], ErrorBudget] = {}

    def create(
        self, installation_id: str, service_id: str,
        slo_target: float, window_requests: int,
    ) -> ErrorBudget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not (90 <= slo_target <= 100):
            raise ValueError("slo_target must be between 90 and 100")
        if window_requests <= 0:
            raise ValueError("window_requests must be positive")

        budget = ErrorBudget(
            service_id=service_id, slo_target=slo_target,
            window_requests=window_requests,
        )
        self._budgets[(installation_id, service_id)] = budget
        return budget

    def record_errors(
        self, installation_id: str, service_id: str, count: int = 1,
    ) -> ErrorBudget:
        b = self._get(installation_id, service_id)
        if count < 0:
            raise ValueError("count must be non-negative")
        b.error_count += count
        return b

    def get(self, installation_id: str, service_id: str) -> ErrorBudget:
        return self._get(installation_id, service_id)

    def exhausted_services(self, installation_id: str) -> list[ErrorBudget]:
        return [
            b for (inst, _), b in self._budgets.items()
            if inst == installation_id and b.is_exhausted
        ]

    def list_budgets(self, installation_id: str) -> list[ErrorBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]

    def reset(self, installation_id: str, service_id: str, new_window: int | None = None) -> ErrorBudget:
        b = self._get(installation_id, service_id)
        b.error_count = 0
        if new_window is not None:
            b.window_requests = new_window
        return b

    def _get(self, installation_id: str, service_id: str) -> ErrorBudget:
        key = (installation_id, service_id)
        b = self._budgets.get(key)
        if b is None:
            raise KeyError(f"Budget for {service_id} not found")
        return b
