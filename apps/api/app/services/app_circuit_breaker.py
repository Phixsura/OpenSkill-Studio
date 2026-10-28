"""App Circuit Breaker — protect downstream services from cascading failures.

Implements the circuit breaker pattern for app-to-service calls:
- States: closed (normal) → open (failing) → half-open (probing)
- Configurable failure threshold and recovery timeout
- Per-service isolated breakers
- Success/failure recording
- Manual reset support
- State history for debugging
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class BreakerConfig:
    """Configuration for a circuit breaker."""

    failure_threshold: int = 5      # failures before opening
    recovery_timeout: float = 30.0  # seconds before half-open probe
    success_threshold: int = 2      # successes in half-open to close


@dataclass
class BreakerStatus:
    """Current status of a circuit breaker."""

    service: str
    state: BreakerState
    failure_count: int
    success_count: int
    last_failure_at: float | None
    opened_at: float | None
    config: BreakerConfig


class AppCircuitBreaker:
    """Per-service circuit breaker manager."""

    def __init__(self, config: BreakerConfig | None = None):
        self._config = config or BreakerConfig()
        self._states: dict[str, BreakerState] = {}
        self._failures: dict[str, int] = {}
        self._successes: dict[str, int] = {}  # half-open successes
        self._last_failure: dict[str, float] = {}
        self._opened_at: dict[str, float] = {}

    def can_execute(self, service: str, now: float | None = None) -> bool:
        """Check if a call to this service is allowed."""
        now = now or time.time()
        state = self._states.get(service, BreakerState.CLOSED)

        if state == BreakerState.CLOSED:
            return True

        if state == BreakerState.OPEN:
            opened = self._opened_at.get(service, 0)
            if now - opened >= self._config.recovery_timeout:
                self._states[service] = BreakerState.HALF_OPEN
                self._successes[service] = 0
                log.info("circuit_breaker.half_open", service=service)
                return True  # allow probe
            return False

        if state == BreakerState.HALF_OPEN:
            return True  # allow probes

        return False

    def record_success(self, service: str) -> BreakerState:
        """Record a successful call."""
        state = self._states.get(service, BreakerState.CLOSED)

        if state == BreakerState.HALF_OPEN:
            self._successes[service] = self._successes.get(service, 0) + 1
            if self._successes[service] >= self._config.success_threshold:
                self._states[service] = BreakerState.CLOSED
                self._failures[service] = 0
                self._successes[service] = 0
                self._opened_at.pop(service, None)
                log.info("circuit_breaker.closed", service=service)
                return BreakerState.CLOSED
            return BreakerState.HALF_OPEN

        # Closed state: reset failure count
        self._failures[service] = 0
        return BreakerState.CLOSED

    def record_failure(self, service: str, now: float | None = None) -> BreakerState:
        """Record a failed call."""
        now = now or time.time()
        state = self._states.get(service, BreakerState.CLOSED)

        if state == BreakerState.HALF_OPEN:
            # Probe failed → reopen
            self._states[service] = BreakerState.OPEN
            self._opened_at[service] = now
            self._last_failure[service] = now
            log.warning("circuit_breaker.reopened", service=service)
            return BreakerState.OPEN

        # Closed state
        self._failures[service] = self._failures.get(service, 0) + 1
        self._last_failure[service] = now

        if self._failures[service] >= self._config.failure_threshold:
            self._states[service] = BreakerState.OPEN
            self._opened_at[service] = now
            log.warning("circuit_breaker.opened", service=service,
                         failures=self._failures[service])
            return BreakerState.OPEN

        return BreakerState.CLOSED

    def get_status(self, service: str) -> BreakerStatus:
        return BreakerStatus(
            service=service,
            state=self._states.get(service, BreakerState.CLOSED),
            failure_count=self._failures.get(service, 0),
            success_count=self._successes.get(service, 0),
            last_failure_at=self._last_failure.get(service),
            opened_at=self._opened_at.get(service),
            config=self._config,
        )

    def reset(self, service: str) -> None:
        """Manually reset a breaker to closed."""
        self._states[service] = BreakerState.CLOSED
        self._failures[service] = 0
        self._successes[service] = 0
        self._opened_at.pop(service, None)
