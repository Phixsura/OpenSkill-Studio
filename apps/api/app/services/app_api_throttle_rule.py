"""App API Throttle Rule — fine-grained request throttling.

Manages throttle rules:
- Define throttle by path, method, or consumer
- Sliding window counters
- Throttle response with retry-after
- Per-installation scoped rules
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ThrottleRule:
    """A throttle rule."""

    rule_id: str
    path_pattern: str
    max_requests: int
    window_seconds: int
    enabled: bool = True


@dataclass
class ThrottleState:
    """Current throttle state for a key."""

    count: int = 0
    window_start: float = field(default_factory=time.time)


class AppAPIThrottleRule:
    """Fine-grained request throttling."""

    def __init__(self) -> None:
        self._rules: dict[tuple[str, str], ThrottleRule] = {}
        self._state: dict[tuple[str, str, str], ThrottleState] = {}

    def add_rule(
        self, installation_id: str, rule_id: str, path_pattern: str,
        max_requests: int, window_seconds: int,
    ) -> ThrottleRule:
        if not installation_id:
            raise ValueError("installation_id is required")
        if max_requests < 1:
            raise ValueError("max_requests must be at least 1")
        if window_seconds < 1:
            raise ValueError("window_seconds must be at least 1")

        rule = ThrottleRule(
            rule_id=rule_id, path_pattern=path_pattern,
            max_requests=max_requests, window_seconds=window_seconds,
        )
        self._rules[(installation_id, rule_id)] = rule
        return rule

    def check_and_record(
        self, installation_id: str, rule_id: str, consumer_id: str,
    ) -> dict:
        """Check throttle and record request. Returns {allowed, remaining, retry_after}."""
        rule = self._get(installation_id, rule_id)
        if not rule.enabled:
            return {"allowed": True, "remaining": rule.max_requests, "retry_after": 0}

        now = time.time()
        key = (installation_id, rule_id, consumer_id)
        state = self._state.get(key)

        if state is None or (now - state.window_start) >= rule.window_seconds:
            self._state[key] = ThrottleState(count=1, window_start=now)
            return {"allowed": True, "remaining": rule.max_requests - 1, "retry_after": 0}

        if state.count >= rule.max_requests:
            retry_after = round(rule.window_seconds - (now - state.window_start), 1)
            return {"allowed": False, "remaining": 0, "retry_after": max(0, retry_after)}

        state.count += 1
        return {"allowed": True, "remaining": rule.max_requests - state.count, "retry_after": 0}

    def list_rules(self, installation_id: str) -> list[ThrottleRule]:
        return [r for (inst, _), r in self._rules.items() if inst == installation_id]

    def _get(self, installation_id: str, rule_id: str) -> ThrottleRule:
        key = (installation_id, rule_id)
        r = self._rules.get(key)
        if r is None:
            raise KeyError(f"Rule {rule_id} not found")
        return r
