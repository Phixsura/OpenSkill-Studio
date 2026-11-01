"""API Consumer Retry Budget — limit total retry attempts across endpoints."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetryBudget:
    consumer_id: str
    budget_per_minute: int = 100
    used_this_minute: int = 0
    total_retries: int = 0
    total_exhausted: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.budget_per_minute - self.used_this_minute)

    @property
    def usage_pct(self) -> float:
        if self.budget_per_minute == 0: return 0.0
        return round((self.used_this_minute / self.budget_per_minute) * 100, 1)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRetryBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], RetryBudget] = {}

    def configure(self, installation_id: str, consumer_id: str, budget_per_minute: int = 100) -> RetryBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if budget_per_minute < 1: raise ValueError("budget must be >= 1")
        b = RetryBudget(consumer_id=consumer_id, budget_per_minute=budget_per_minute)
        self._budgets[(installation_id, consumer_id)] = b
        return b

    def try_retry(self, installation_id: str, consumer_id: str) -> bool:
        b = self._budgets.get((installation_id, consumer_id))
        if b is None: return True  # no budget = allow
        if b.used_this_minute >= b.budget_per_minute:
            b.total_exhausted += 1
            return False
        b.used_this_minute += 1
        b.total_retries += 1
        return True

    def reset_minute(self, installation_id: str, consumer_id: str) -> RetryBudget:
        b = self._budgets.get((installation_id, consumer_id))
        if b is None: raise KeyError(f"No budget for {consumer_id}")
        b.used_this_minute = 0
        return b

    def get_budget(self, installation_id: str, consumer_id: str) -> RetryBudget | None:
        return self._budgets.get((installation_id, consumer_id))

    def list_budgets(self, installation_id: str) -> list[RetryBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
