"""App Webhook Retry Policy — configurable retry strategies for webhook delivery.

Manages retry policies for webhook delivery:
- Define policies per webhook (max retries, backoff strategy)
- Compute next retry delay
- Track retry attempts
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import structlog

log = structlog.get_logger()


class BackoffStrategy(str, Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


@dataclass
class RetryPolicy:
    """A webhook retry policy."""

    policy_id: str
    max_retries: int = 5
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    base_delay_seconds: float = 10.0
    max_delay_seconds: float = 3600.0


@dataclass
class RetrySchedule:
    """Computed retry schedule."""

    attempt: int
    delay_seconds: float
    should_retry: bool


class AppWebhookRetryPolicy:
    """Configurable retry strategies for webhook delivery."""

    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], RetryPolicy] = {}

    def create_policy(
        self,
        installation_id: str,
        policy_id: str,
        max_retries: int = 5,
        strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
        base_delay_seconds: float = 10.0,
        max_delay_seconds: float = 3600.0,
    ) -> RetryPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not policy_id:
            raise ValueError("policy_id is required")
        if max_retries < 1:
            raise ValueError("max_retries must be >= 1")

        policy = RetryPolicy(
            policy_id=policy_id, max_retries=max_retries,
            strategy=strategy, base_delay_seconds=base_delay_seconds,
            max_delay_seconds=max_delay_seconds,
        )
        self._policies[(installation_id, policy_id)] = policy
        return policy

    def compute_retry(
        self, installation_id: str, policy_id: str, attempt: int
    ) -> RetrySchedule:
        """Compute whether and when to retry."""
        policy = self._get(installation_id, policy_id)

        if attempt >= policy.max_retries:
            return RetrySchedule(attempt=attempt, delay_seconds=0, should_retry=False)

        if policy.strategy == BackoffStrategy.FIXED:
            delay = policy.base_delay_seconds
        elif policy.strategy == BackoffStrategy.LINEAR:
            delay = policy.base_delay_seconds * (attempt + 1)
        else:  # exponential
            delay = policy.base_delay_seconds * (2 ** attempt)

        delay = min(delay, policy.max_delay_seconds)
        return RetrySchedule(attempt=attempt, delay_seconds=round(delay, 1), should_retry=True)

    def get_full_schedule(self, installation_id: str, policy_id: str) -> list[RetrySchedule]:
        """Get the full retry schedule."""
        policy = self._get(installation_id, policy_id)
        return [self.compute_retry(installation_id, policy_id, i) for i in range(policy.max_retries + 1)]

    def get_policy(self, installation_id: str, policy_id: str) -> RetryPolicy:
        return self._get(installation_id, policy_id)

    def list_policies(self, installation_id: str) -> list[RetryPolicy]:
        return [p for (inst, _), p in self._policies.items() if inst == installation_id]

    def _get(self, installation_id: str, policy_id: str) -> RetryPolicy:
        key = (installation_id, policy_id)
        p = self._policies.get(key)
        if p is None:
            raise KeyError(f"Policy {policy_id} not found")
        return p
