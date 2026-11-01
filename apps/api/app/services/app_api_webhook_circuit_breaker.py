"""App API Webhook Circuit Breaker — per-destination circuit breaking.

Manages per-destination circuit breakers:
- Open circuit on consecutive failures
- Half-open probe after cooldown
- Auto-close on successful probe
- Per-installation scoped breakers
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from enum import Enum

import structlog

log = structlog.get_logger()


class CBState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class DestinationBreaker:
    """Circuit breaker for a webhook destination."""

    destination: str
    state: CBState = CBState.CLOSED
    consecutive_failures: int = 0
    failure_threshold: int = 5
    cooldown_seconds: float = 60.0
    opened_at: float | None = None


class AppAPIWebhookCircuitBreaker:
    """Per-destination circuit breaking."""

    def __init__(self, failure_threshold: int = 5, cooldown_seconds: float = 60.0) -> None:
        self._threshold = failure_threshold
        self._cooldown = cooldown_seconds
        self._breakers: dict[tuple[str, str], DestinationBreaker] = {}

    def record_success(self, installation_id: str, destination: str) -> DestinationBreaker:
        b = self._get_or_create(installation_id, destination)
        b.consecutive_failures = 0
        if b.state == CBState.HALF_OPEN:
            b.state = CBState.CLOSED
        return b

    def record_failure(self, installation_id: str, destination: str) -> DestinationBreaker:
        b = self._get_or_create(installation_id, destination)
        b.consecutive_failures += 1
        if b.state == CBState.HALF_OPEN:
            b.state = CBState.OPEN
            b.opened_at = time.time()
        elif b.consecutive_failures >= b.failure_threshold:
            b.state = CBState.OPEN
            b.opened_at = time.time()
        return b

    def should_allow(self, installation_id: str, destination: str) -> bool:
        b = self._breakers.get((installation_id, destination))
        if b is None:
            return True
        if b.state == CBState.CLOSED:
            return True
        if b.state == CBState.OPEN and b.opened_at:
            if (time.time() - b.opened_at) >= b.cooldown_seconds:
                b.state = CBState.HALF_OPEN
                return True
            return False
        return True  # half_open allows probe

    def open_breakers(self, installation_id: str) -> list[DestinationBreaker]:
        return [b for (inst, _), b in self._breakers.items() if inst == installation_id and b.state == CBState.OPEN]

    def _get_or_create(self, installation_id: str, destination: str) -> DestinationBreaker:
        key = (installation_id, destination)
        if key not in self._breakers:
            self._breakers[key] = DestinationBreaker(
                destination=destination, failure_threshold=self._threshold, cooldown_seconds=self._cooldown,
            )
        return self._breakers[key]
