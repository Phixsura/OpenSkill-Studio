"""App Retry Policy Engine — compute retry delays with configurable strategies.

Computes retry timing for failed app operations:
- Strategies: fixed, linear, exponential, exponential with jitter
- Max retry limit enforcement
- Per-operation retry state tracking
- Deadline support (absolute timeout)
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class RetryStrategy(str, Enum):
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    EXPONENTIAL_JITTER = "exponential_jitter"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    max_retries: int = 5
    multiplier: float = 2.0
    deadline_seconds: float | None = None  # absolute time limit


@dataclass
class RetryState:
    """Tracks retry state for an operation."""

    operation_id: str
    attempt: int = 0
    first_attempt_at: float = field(default_factory=time.time)
    last_attempt_at: float | None = None
    exhausted: bool = False


@dataclass
class RetryDecision:
    """Result of computing next retry."""

    should_retry: bool
    delay_seconds: float = 0.0
    attempt: int = 0
    reason: str = ""


def _deterministic_jitter(operation_id: str, attempt: int) -> float:
    """Deterministic jitter factor 0.5-1.5 based on operation + attempt."""
    h = hashlib.sha256(f"{operation_id}:{attempt}".encode()).hexdigest()
    return 0.5 + (int(h[:4], 16) % 1000) / 1000.0


class AppRetryPolicyEngine:
    """Compute retry delays with configurable strategies."""

    def __init__(self, config: RetryConfig | None = None) -> None:
        self._config = config or RetryConfig()
        self._states: dict[str, RetryState] = {}

    def record_attempt(self, operation_id: str, now: float | None = None) -> RetryState:
        """Record an attempt for an operation."""
        now = now or time.time()

        if operation_id not in self._states:
            self._states[operation_id] = RetryState(
                operation_id=operation_id,
                attempt=1,
                first_attempt_at=now,
                last_attempt_at=now,
            )
        else:
            state = self._states[operation_id]
            state.attempt += 1
            state.last_attempt_at = now
            if state.attempt > self._config.max_retries:
                state.exhausted = True

        return self._states[operation_id]

    def should_retry(self, operation_id: str, now: float | None = None) -> RetryDecision:
        """Compute whether and when to retry."""
        now = now or time.time()
        state = self._states.get(operation_id)

        if state is None:
            return RetryDecision(should_retry=True, delay_seconds=0.0,
                                 attempt=0, reason="first_attempt")

        if state.exhausted or state.attempt >= self._config.max_retries:
            state.exhausted = True
            return RetryDecision(should_retry=False, attempt=state.attempt,
                                 reason="max_retries_exceeded")

        # Check deadline
        if self._config.deadline_seconds is not None:
            elapsed = now - state.first_attempt_at
            if elapsed >= self._config.deadline_seconds:
                state.exhausted = True
                return RetryDecision(should_retry=False, attempt=state.attempt,
                                     reason="deadline_exceeded")

        delay = self._compute_delay(operation_id, state.attempt)

        return RetryDecision(
            should_retry=True,
            delay_seconds=delay,
            attempt=state.attempt,
        )

    def get_state(self, operation_id: str) -> RetryState | None:
        return self._states.get(operation_id)

    def reset(self, operation_id: str) -> None:
        """Reset retry state for an operation."""
        self._states.pop(operation_id, None)

    def _compute_delay(self, operation_id: str, attempt: int) -> float:
        cfg = self._config

        if cfg.strategy == RetryStrategy.FIXED:
            delay = cfg.base_delay_seconds

        elif cfg.strategy == RetryStrategy.LINEAR:
            delay = cfg.base_delay_seconds * attempt

        elif cfg.strategy == RetryStrategy.EXPONENTIAL:
            delay = cfg.base_delay_seconds * (cfg.multiplier ** (attempt - 1))

        elif cfg.strategy == RetryStrategy.EXPONENTIAL_JITTER:
            base = cfg.base_delay_seconds * (cfg.multiplier ** (attempt - 1))
            jitter = _deterministic_jitter(operation_id, attempt)
            delay = base * jitter

        else:
            delay = cfg.base_delay_seconds

        return min(delay, cfg.max_delay_seconds)
