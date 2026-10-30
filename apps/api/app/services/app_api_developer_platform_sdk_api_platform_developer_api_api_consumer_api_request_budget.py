"""API Consumer Request Budget — allocate and track request budgets per period."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RequestBudget:
    consumer_id: str
    period: str  # "2024-01"
    allocated: int
    used: int = 0
    rollover: int = 0  # unused from previous period

    @property
    def remaining(self) -> int:
        return max(0, self.allocated + self.rollover - self.used)

    @property
    def usage_pct(self) -> float:
        total = self.allocated + self.rollover
        if total == 0: return 0.0
        return round((self.used / total) * 100, 1)

    @property
    def exhausted(self) -> bool:
        return self.used >= self.allocated + self.rollover

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str, str], RequestBudget] = {}

    def allocate(self, installation_id: str, consumer_id: str, period: str, amount: int, rollover: int = 0) -> RequestBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if amount < 1: raise ValueError("amount must be >= 1")
        if rollover < 0: raise ValueError("rollover must be non-negative")
        key = (installation_id, consumer_id, period)
        if key in self._budgets: raise ValueError(f"Budget for {consumer_id}/{period} exists")
        b = RequestBudget(consumer_id=consumer_id, period=period, allocated=amount, rollover=rollover)
        self._budgets[key] = b
        return b

    def consume(self, installation_id: str, consumer_id: str, period: str, count: int = 1) -> RequestBudget:
        key = (installation_id, consumer_id, period)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {consumer_id}/{period}")
        if count < 1: raise ValueError("count must be >= 1")
        if count > b.remaining: raise ValueError("Budget exhausted")
        b.used += count
        return b

    def get_budget(self, installation_id: str, consumer_id: str, period: str) -> RequestBudget:
        b = self._budgets.get((installation_id, consumer_id, period))
        if b is None: raise KeyError(f"No budget for {consumer_id}/{period}")
        return b

    def near_exhaustion(self, installation_id: str, threshold_pct: float = 90.0) -> list[RequestBudget]:
        return [b for (inst, _, _), b in self._budgets.items() if inst == installation_id and b.usage_pct >= threshold_pct and not b.exhausted]

    def list_budgets(self, installation_id: str) -> list[RequestBudget]:
        return [b for (inst, _, _), b in self._budgets.items() if inst == installation_id]
