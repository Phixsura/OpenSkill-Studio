"""App Cost Tracker — track and allocate infrastructure costs per installation.

Manages cost tracking for installed apps:
- Record cost entries by category
- Compute total costs per period
- Cost allocation across categories
- Per-installation scoped costs
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CostEntry:
    """A cost record."""

    entry_id: str
    category: str  # compute, storage, network, api_calls
    amount_cents: int
    description: str = ""
    timestamp: float = field(default_factory=time.time)


class AppCostTracker:
    """Track and allocate infrastructure costs."""

    def __init__(self) -> None:
        self._entries: dict[str, list[CostEntry]] = {}

    def record_cost(
        self,
        installation_id: str,
        entry_id: str,
        category: str,
        amount_cents: int,
        description: str = "",
        now: float | None = None,
    ) -> CostEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not category:
            raise ValueError("category is required")
        if amount_cents < 0:
            raise ValueError("amount_cents must be non-negative")

        entry = CostEntry(
            entry_id=entry_id, category=category,
            amount_cents=amount_cents, description=description,
            timestamp=now or time.time(),
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def total_cents(self, installation_id: str, since: float | None = None) -> int:
        entries = self._entries.get(installation_id, [])
        if since is not None:
            entries = [e for e in entries if e.timestamp >= since]
        return sum(e.amount_cents for e in entries)

    def total_dollars(self, installation_id: str, since: float | None = None) -> float:
        return self.total_cents(installation_id, since) / 100

    def by_category(self, installation_id: str) -> dict[str, int]:
        """Cost breakdown by category in cents."""
        result: dict[str, int] = {}
        for e in self._entries.get(installation_id, []):
            result[e.category] = result.get(e.category, 0) + e.amount_cents
        return result

    def get_entries(
        self, installation_id: str, category: str | None = None, limit: int = 50
    ) -> list[CostEntry]:
        entries = self._entries.get(installation_id, [])
        if category:
            entries = [e for e in entries if e.category == category]
        return list(reversed(entries[-limit:]))

    def entry_count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
