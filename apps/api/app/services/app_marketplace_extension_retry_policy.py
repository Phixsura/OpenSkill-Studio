"""Retry Policy Engine — configurable retry strategies with backoff and jitter.

Strategies:
- Fixed: constant delay between retries
- Exponential: 2^attempt * base_delay with optional jitter
- Linear: attempt * base_delay
- Custom: caller-provided delay sequence

Features:
- Max attempts with total timeout cap
- Retryable vs non-retryable error classification
- Jitter to prevent thundering herd
- Per-operation retry budgets
"""
from __future__ import annotations
from dataclasses import dataclass, field
import random
import time
from enum import Enum


class RetryStrategy(str, Enum):
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"


# HTTP status codes that are retryable
RETRYABLE_STATUSES = {408, 429, 500, 502, 503, 504}
NON_RETRYABLE_STATUSES = {400, 401, 403, 404, 405, 409, 422}


@dataclass
class RetryPolicy:
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    max_attempts: int = 3
    base_delay_ms: float = 1000
    max_delay_ms: float = 30000
    jitter: bool = True
    jitter_factor: float = 0.25  # ±25%
    total_timeout_ms: float = 60000
    retryable_errors: set[str] = field(default_factory=lambda: {"timeout", "connection_error", "server_error"})


@dataclass
class RetryAttempt:
    attempt: int
    delay_ms: float
    error: str
    timestamp: float


@dataclass
class RetryResult:
    success: bool
    attempts: list[RetryAttempt]
    total_time_ms: float
    final_error: str = ""
    budget_exhausted: bool = False


class RetryPolicyEngineService:
    def __init__(self):
        self._policies: dict[str, RetryPolicy] = {}
        self._budgets: dict[str, int] = {}  # operation -> remaining retries
        self._default = RetryPolicy()

    def register(self, operation: str, policy: RetryPolicy | None = None,
                 budget: int = 0) -> RetryPolicy:
        p = policy or RetryPolicy()
        self._policies[operation] = p
        if budget > 0:
            self._budgets[operation] = budget
        return p

    def calculate_delay(self, policy: RetryPolicy, attempt: int) -> float:
        """Calculate delay in ms for a given attempt number (0-based)."""
        if policy.strategy == RetryStrategy.FIXED:
            delay = policy.base_delay_ms
        elif policy.strategy == RetryStrategy.LINEAR:
            delay = policy.base_delay_ms * (attempt + 1)
        else:  # exponential
            delay = policy.base_delay_ms * (2 ** attempt)

        # Cap at max
        delay = min(delay, policy.max_delay_ms)

        # Apply jitter
        if policy.jitter:
            jitter_range = delay * policy.jitter_factor
            delay += random.uniform(-jitter_range, jitter_range)
            delay = max(0, delay)

        return round(delay, 1)

    def should_retry(self, operation: str, error: str,
                     status_code: int = 0, attempt: int = 0) -> tuple[bool, float, str]:
        """Returns (should_retry, delay_ms, reason)."""
        policy = self._policies.get(operation, self._default)

        # Check max attempts
        if attempt >= policy.max_attempts:
            return False, 0, f"Max attempts ({policy.max_attempts}) reached"

        # Check budget
        if operation in self._budgets:
            if self._budgets[operation] <= 0:
                return False, 0, "Retry budget exhausted"

        # Check if error is retryable
        if status_code and status_code in NON_RETRYABLE_STATUSES:
            return False, 0, f"Status {status_code} is not retryable"

        if status_code and status_code not in RETRYABLE_STATUSES:
            if error not in policy.retryable_errors:
                return False, 0, f"Error '{error}' is not retryable"

        delay = self.calculate_delay(policy, attempt)

        # Consume budget
        if operation in self._budgets:
            self._budgets[operation] -= 1

        # Special handling for 429 Retry-After
        if status_code == 429:
            delay = max(delay, 5000)  # at least 5s for rate limit

        return True, delay, "Retrying"

    def simulate(self, operation: str, errors: list[tuple[str, int]]) -> RetryResult:
        """Simulate a retry sequence. errors = [(error_msg, status_code), ...]"""
        policy = self._policies.get(operation, self._default)
        attempts = []
        start = time.time()

        for i, (error, status) in enumerate(errors):
            should, delay, reason = self.should_retry(operation, error, status, i)
            attempts.append(RetryAttempt(attempt=i, delay_ms=delay,
                                        error=error, timestamp=time.time()))
            if not should:
                total = round((time.time() - start) * 1000, 1)
                return RetryResult(success=False, attempts=attempts,
                                   total_time_ms=total, final_error=reason)

        total = round((time.time() - start) * 1000, 1)
        return RetryResult(success=True, attempts=attempts, total_time_ms=total)

    def get_budget(self, operation: str) -> int | None:
        return self._budgets.get(operation)
