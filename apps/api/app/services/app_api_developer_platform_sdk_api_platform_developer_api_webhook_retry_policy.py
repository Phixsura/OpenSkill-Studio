"""API Webhook Retry Policy — configurable retry strategies for webhook delivery."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger()

class RetryStrategy(str, Enum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"

@dataclass
class RetryPolicy:
    policy_id: str
    consumer_id: str
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_retries: int = 5
    base_delay_s: int = 10
    max_delay_s: int = 3600
    jitter: bool = True

    def delay_for_attempt(self, attempt: int) -> int:
        if attempt < 1: return 0
        if self.strategy == RetryStrategy.FIXED:
            d = self.base_delay_s
        elif self.strategy == RetryStrategy.LINEAR:
            d = self.base_delay_s * attempt
        else:  # exponential
            d = self.base_delay_s * (2 ** (attempt - 1))
        return min(d, self.max_delay_s)

@dataclass
class DeliveryAttempt:
    event_id: str
    attempt: int
    status_code: int
    success: bool
    next_retry_delay_s: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookRetryPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RetryPolicy] = {}
        self._attempts: dict[tuple[str, str], list[DeliveryAttempt]] = {}

    def set_policy(self, installation_id: str, policy: RetryPolicy) -> RetryPolicy:
        if not installation_id: raise ValueError("installation_id is required")
        if policy.max_retries < 0: raise ValueError("max_retries must be non-negative")
        if policy.base_delay_s < 1: raise ValueError("base_delay must be >= 1s")
        self._policies[(installation_id, policy.consumer_id)] = policy
        return policy

    def record_attempt(self, installation_id: str, consumer_id: str, event_id: str, attempt: int, status_code: int) -> DeliveryAttempt:
        policy = self._policies.get((installation_id, consumer_id))
        if policy is None: raise KeyError(f"No policy for {consumer_id}")
        success = 200 <= status_code < 300
        next_delay = 0
        if not success and attempt < policy.max_retries:
            next_delay = policy.delay_for_attempt(attempt + 1)
        da = DeliveryAttempt(event_id=event_id, attempt=attempt, status_code=status_code, success=success, next_retry_delay_s=next_delay)
        self._attempts.setdefault((installation_id, event_id), []).append(da)
        return da

    def should_retry(self, installation_id: str, consumer_id: str, attempt: int) -> bool:
        policy = self._policies.get((installation_id, consumer_id))
        if policy is None: return False
        return attempt < policy.max_retries

    def get_policy(self, installation_id: str, consumer_id: str) -> RetryPolicy | None:
        return self._policies.get((installation_id, consumer_id))

    def list_policies(self, installation_id: str) -> list[RetryPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]
