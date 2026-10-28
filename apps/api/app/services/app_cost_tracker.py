"""App Cost Tracker — track API and resource usage costs.

Manages cost tracking for installed apps:
- Record cost entries by category
- Daily/monthly aggregation
- Budget alerts when spending exceeds threshold
- Per-installation scoped costs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CostEntry:
    """A single cost entry."""

    entry_id: str
    category: str  # "compute", "storage", "api_calls", "bandwidth"
    amount: float
    currency: str = "USD"
    description: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class CostBudget:
    """A spending budget."""

    category: str
    monthly_limit: float
    currency: str = "USD"


class AppCostTracker:
    """Track API and resource usage costs."""

    def __init__(self) -> None:
        self._entries: dict[str, list[CostEntry]] = {}
        self._budgets: dict[tuple[str, str], CostBudget] = {}

    def record(
        self, installation_id: str, entry_id: str, category: str,
        amount: float, currency: str = "USD", description: str = "",
    ) -> CostEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if not category:
            raise ValueError("category is required")

        entry = CostEntry(
            entry_id=entry_id, category=category, amount=amount,
            currency=currency, description=description,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def total(self, installation_id: str, category: str | None = None) -> float:
        entries = self._entries.get(installation_id, [])
        if category:
            entries = [e for e in entries if e.category == category]
        return round(sum(e.amount for e in entries), 2)

    def by_category(self, installation_id: str) -> dict[str, float]:
        entries = self._entries.get(installation_id, [])
        cats: dict[str, float] = {}
        for e in entries:
            cats[e.category] = round(cats.get(e.category, 0) + e.amount, 2)
        return cats

    def set_budget(
        self, installation_id: str, category: str, monthly_limit: float,
        currency: str = "USD",
    ) -> CostBudget:
        if monthly_limit <= 0:
            raise ValueError("monthly_limit must be positive")
        budget = CostBudget(category=category, monthly_limit=monthly_limit, currency=currency)
        self._budgets[(installation_id, category)] = budget
        return budget

    def budget_alerts(self, installation_id: str, threshold_pct: float = 80.0) -> list[dict]:
        alerts = []
        for (inst, cat), budget in self._budgets.items():
            if inst != installation_id:
                continue
            spent = self.total(installation_id, cat)
            pct = round(spent / budget.monthly_limit * 100, 1) if budget.monthly_limit > 0 else 0
            if pct >= threshold_pct:
                alerts.append({
                    "category": cat, "spent": spent,
                    "limit": budget.monthly_limit, "pct": pct,
                })
        return alerts

    def recent(self, installation_id: str, limit: int = 20) -> list[CostEntry]:
        entries = self._entries.get(installation_id, [])
        return list(reversed(entries[-limit:]))
