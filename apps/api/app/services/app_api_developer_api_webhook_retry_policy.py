"""App API Developer Webhook Retry Policy — configurable retry strategies."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RetryPolicy:
    policy_id: str
    max_retries: int
    base_delay_seconds: int
    max_delay_seconds: int
    backoff_multiplier: float = 2.0
    strategy: str = "exponential"  # "exponential", "linear", "fixed"

    def delay_for_attempt(self, attempt: int) -> int:
        if attempt < 1: return 0
        if self.strategy == "fixed":
            d = self.base_delay_seconds
        elif self.strategy == "linear":
            d = self.base_delay_seconds * attempt
        else:
            d = int(self.base_delay_seconds * (self.backoff_multiplier ** (attempt - 1)))
        return min(d, self.max_delay_seconds)

class AppAPIDeveloperAPIWebhookRetryPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RetryPolicy] = {}

    def create(self, installation_id: str, policy_id: str, max_retries: int = 3, base_delay_seconds: int = 10, max_delay_seconds: int = 3600, backoff_multiplier: float = 2.0, strategy: str = "exponential") -> RetryPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if max_retries < 0: raise ValueError("max_retries must be non-negative")
        if strategy not in ("exponential", "linear", "fixed"): raise ValueError("invalid strategy")
        key = (installation_id, policy_id)
        if key in self._policies: raise ValueError(f"Policy {policy_id} exists")
        p = RetryPolicy(policy_id=policy_id, max_retries=max_retries, base_delay_seconds=base_delay_seconds, max_delay_seconds=max_delay_seconds, backoff_multiplier=backoff_multiplier, strategy=strategy)
        self._policies[key] = p
        return p

    def get(self, installation_id: str, policy_id: str) -> RetryPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None: raise KeyError(f"Policy {policy_id} not found")
        return p

    def schedule(self, installation_id: str, policy_id: str) -> list[int]:
        p = self.get(installation_id, policy_id)
        return [p.delay_for_attempt(i) for i in range(1, p.max_retries + 1)]

    def list_policies(self, installation_id: str) -> list[RetryPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
