"""App API Developer Webhook Retry Budget — limit retry resources per destination."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetryBudget:
    destination: str
    max_retries_per_hour: int
    retries_used: int = 0
    budget_resets_remaining: int = 0

    @property
    def remaining(self) -> int:
        return max(0, self.max_retries_per_hour - self.retries_used)

    @property
    def usage_pct(self) -> float:
        return round(self.retries_used / self.max_retries_per_hour * 100, 1) if self.max_retries_per_hour > 0 else 0.0

    @property
    def exhausted(self) -> bool:
        return self.retries_used >= self.max_retries_per_hour

class AppAPIDeveloperPlatformSDKApiWebhookRetryBudget:
    def __init__(self) -> None:
        self._budgets: dict[tuple[str, str], RetryBudget] = {}

    def set_budget(self, installation_id: str, destination: str, max_retries_per_hour: int) -> RetryBudget:
        if not installation_id: raise ValueError("installation_id is required")
        if max_retries_per_hour < 1: raise ValueError("max must be >= 1")
        key = (installation_id, destination)
        b = RetryBudget(destination=destination, max_retries_per_hour=max_retries_per_hour)
        self._budgets[key] = b
        return b

    def use_retry(self, installation_id: str, destination: str) -> RetryBudget:
        key = (installation_id, destination)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {destination}")
        if b.exhausted: raise ValueError("Retry budget exhausted")
        b.retries_used += 1
        return b

    def reset(self, installation_id: str, destination: str) -> RetryBudget:
        key = (installation_id, destination)
        b = self._budgets.get(key)
        if b is None: raise KeyError(f"No budget for {destination}")
        b.budget_resets_remaining = b.retries_used
        b.retries_used = 0
        return b

    def exhausted_destinations(self, installation_id: str) -> list[RetryBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id and b.exhausted]

    def all_budgets(self, installation_id: str) -> list[RetryBudget]:
        return [b for (inst, _), b in self._budgets.items() if inst == installation_id]
