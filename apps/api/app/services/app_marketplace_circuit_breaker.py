"""Circuit Breaker — protect platform from cascading extension failures.

Implements the circuit breaker pattern: tracks failure rates per extension
and opens the circuit (blocks calls) when failures exceed a threshold,
with automatic recovery via half-open state.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"      # normal operation
    OPEN = "open"          # blocking calls
    HALF_OPEN = "half_open"  # testing recovery


@dataclass
class CircuitStats:
    successes: int = 0
    failures: int = 0
    consecutive_failures: int = 0
    last_failure_at: float = 0.0
    last_state_change: float = 0.0


class CircuitBreaker:
    """Circuit breaker for extension API calls."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: float = 30.0,
                 half_open_max_calls: int = 3):
        self._circuits: dict[str, CircuitState] = {}
        self._stats: dict[str, CircuitStats] = {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max = half_open_max_calls
        self._half_open_calls: dict[str, int] = {}

    def _get_state(self, key: str) -> CircuitState:
        state = self._circuits.get(key, CircuitState.CLOSED)
        if state == CircuitState.OPEN:
            stats = self._stats.get(key, CircuitStats())
            if time.monotonic() - stats.last_state_change > self._recovery_timeout:
                self._circuits[key] = CircuitState.HALF_OPEN
                self._half_open_calls[key] = 0
                return CircuitState.HALF_OPEN
        return state

    def allow_request(self, key: str) -> tuple[bool, CircuitState]:
        """Check if a request should be allowed through."""
        state = self._get_state(key)
        if state == CircuitState.CLOSED:
            return True, state
        if state == CircuitState.OPEN:
            return False, state
        # Half-open: allow limited calls
        calls = self._half_open_calls.get(key, 0)
        if calls < self._half_open_max:
            self._half_open_calls[key] = calls + 1
            return True, state
        return False, state

    def record_success(self, key: str) -> None:
        """Record a successful call."""
        stats = self._stats.setdefault(key, CircuitStats())
        stats.successes += 1
        stats.consecutive_failures = 0
        state = self._get_state(key)
        if state == CircuitState.HALF_OPEN:
            # Enough successes in half-open → close circuit
            self._circuits[key] = CircuitState.CLOSED
            stats.last_state_change = time.monotonic()

    def record_failure(self, key: str) -> CircuitState:
        """Record a failed call. May trip the circuit."""
        stats = self._stats.setdefault(key, CircuitStats())
        stats.failures += 1
        stats.consecutive_failures += 1
        stats.last_failure_at = time.monotonic()

        state = self._get_state(key)
        if state == CircuitState.HALF_OPEN:
            # Failure during recovery → open again
            self._circuits[key] = CircuitState.OPEN
            stats.last_state_change = time.monotonic()
            return CircuitState.OPEN

        if stats.consecutive_failures >= self._failure_threshold:
            self._circuits[key] = CircuitState.OPEN
            stats.last_state_change = time.monotonic()
            return CircuitState.OPEN

        return CircuitState.CLOSED

    def get_state(self, key: str) -> CircuitState:
        return self._get_state(key)

    def get_stats(self, key: str) -> dict:
        stats = self._stats.get(key, CircuitStats())
        return {
            "key": key, "state": self._get_state(key).value,
            "successes": stats.successes, "failures": stats.failures,
            "consecutive_failures": stats.consecutive_failures,
        }

    def reset(self, key: str) -> None:
        self._circuits.pop(key, None)
        self._stats.pop(key, None)
        self._half_open_calls.pop(key, None)
