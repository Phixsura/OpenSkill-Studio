"""App API Performance Budget — set and track performance budgets.

Manages performance budgets:
- Define budgets for response time, payload size, etc.
- Check current values against budgets
- Track violations over time
- Per-installation scoped budgets
"""

from __future__ import annotations

from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class PerfBudget:
    """A performance budget."""

    budget_id: str
    metric: str  # "response_time_ms", "payload_size_kb", "ttfb_ms"
    max_value: float
    current_value: float = 0.0
    violations: int = 0

    @property
    def within_budget(self) -> bool:
        return self.current_value <= self.max_value

    @property
    def usage_pct(self) -> float:
        if self.max_value == 0:
            return 0.0
        return round(self.current_value / self.max_value * 100, 1)


class AppAPIPerformanceBudget:
    """Set and track performance budgets."""

    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], PerfBudget] = {}

    def set_budget(
        self, installation_id: str, budget_id: str, metric: str, max_value: float,
    ) -> PerfBudget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if max_value <= 0:
            raise ValueError("max_value must be positive")

        b = PerfBudget(budget_id=budget_id, metric=metric, max_value=max_value)
        self._budgets[(installation_id, budget_id)] = b
        return b

    def record(self, installation_id: str, budget_id: str, value: float) -> PerfBudget:
        b = self._get(installation_id, budget_id)
        b.current_value = value
        if value > b.max_value:
            b.violations += 1
        return b

    def violations(self, installation_id: str) -> list[PerfBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and not b.within_budget]

    def list_budgets(self, installation_id: str) -> list[PerfBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]

    def _get(self, installation_id: str, budget_id: str) -> PerfBudget:
        key = (installation_id, budget_id)
        b = self._budgets.get(key)
        if b is None:
            raise KeyError(f"Budget {budget_id} not found")
        return b
