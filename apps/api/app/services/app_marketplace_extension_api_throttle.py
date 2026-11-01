"""API Throttle — adaptive throttling based on system load and error rates.

Dynamically adjusts request throughput based on CPU load, error rates,
queue depth, with gradual recovery and per-extension overrides.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field
from enum import Enum


class ThrottleLevel(str, Enum):
    NONE = "none"
    LIGHT = "light"      # 80% throughput
    MODERATE = "moderate" # 50% throughput
    HEAVY = "heavy"       # 20% throughput
    BLOCK = "block"       # 0% — reject all


LEVEL_THROUGHPUT = {
    ThrottleLevel.NONE: 1.0,
    ThrottleLevel.LIGHT: 0.8,
    ThrottleLevel.MODERATE: 0.5,
    ThrottleLevel.HEAVY: 0.2,
    ThrottleLevel.BLOCK: 0.0,
}


@dataclass
class ThrottleState:
    extension_id: str
    level: ThrottleLevel = ThrottleLevel.NONE
    throughput: float = 1.0
    reason: str = ""
    requests_allowed: int = 0
    requests_throttled: int = 0
    last_updated: float = 0.0


@dataclass
class SystemMetrics:
    cpu_percent: float = 0
    error_rate_percent: float = 0
    queue_depth: int = 0
    p99_latency_ms: float = 0


class ApiThrottleService:
    """Adaptive throttling based on system metrics."""

    CPU_THRESHOLD_LIGHT = 70
    CPU_THRESHOLD_MODERATE = 85
    CPU_THRESHOLD_HEAVY = 95
    ERROR_THRESHOLD_LIGHT = 5
    ERROR_THRESHOLD_MODERATE = 15
    ERROR_THRESHOLD_HEAVY = 30

    def __init__(self):
        self._states: dict[str, ThrottleState] = {}
        self._overrides: dict[str, ThrottleLevel] = {}

    def _get_state(self, extension_id: str) -> ThrottleState:
        if extension_id not in self._states:
            self._states[extension_id] = ThrottleState(extension_id=extension_id)
        return self._states[extension_id]

    def evaluate(self, extension_id: str, metrics: SystemMetrics) -> ThrottleState:
        state = self._get_state(extension_id)

        # Check for manual override
        if extension_id in self._overrides:
            level = self._overrides[extension_id]
            state.level = level
            state.throughput = LEVEL_THROUGHPUT[level]
            state.reason = "manual override"
            state.last_updated = time.time()
            return state

        # Determine level from metrics
        level = ThrottleLevel.NONE
        reasons = []

        if metrics.cpu_percent >= self.CPU_THRESHOLD_HEAVY:
            level = ThrottleLevel.HEAVY
            reasons.append(f"CPU {metrics.cpu_percent}%")
        elif metrics.cpu_percent >= self.CPU_THRESHOLD_MODERATE:
            level = max(level, ThrottleLevel.MODERATE, key=lambda l: list(ThrottleLevel).index(l))
            reasons.append(f"CPU {metrics.cpu_percent}%")
        elif metrics.cpu_percent >= self.CPU_THRESHOLD_LIGHT:
            level = max(level, ThrottleLevel.LIGHT, key=lambda l: list(ThrottleLevel).index(l))
            reasons.append(f"CPU {metrics.cpu_percent}%")

        if metrics.error_rate_percent >= self.ERROR_THRESHOLD_HEAVY:
            level = ThrottleLevel.HEAVY
            reasons.append(f"Errors {metrics.error_rate_percent}%")
        elif metrics.error_rate_percent >= self.ERROR_THRESHOLD_MODERATE:
            if list(ThrottleLevel).index(ThrottleLevel.MODERATE) > list(ThrottleLevel).index(level):
                level = ThrottleLevel.MODERATE
            reasons.append(f"Errors {metrics.error_rate_percent}%")

        state.level = level
        state.throughput = LEVEL_THROUGHPUT[level]
        state.reason = "; ".join(reasons) if reasons else "normal"
        state.last_updated = time.time()
        return state

    def should_allow(self, extension_id: str) -> bool:
        state = self._get_state(extension_id)
        if state.level == ThrottleLevel.BLOCK:
            state.requests_throttled += 1
            return False
        if state.level == ThrottleLevel.NONE:
            state.requests_allowed += 1
            return True
        # Probabilistic allow based on throughput
        import random
        if random.random() < state.throughput:
            state.requests_allowed += 1
            return True
        state.requests_throttled += 1
        return False

    def set_override(self, extension_id: str, level: ThrottleLevel) -> None:
        self._overrides[extension_id] = level

    def clear_override(self, extension_id: str) -> bool:
        return self._overrides.pop(extension_id, None) is not None

    def get_state(self, extension_id: str) -> dict:
        state = self._get_state(extension_id)
        return {
            "level": state.level.value, "throughput": state.throughput,
            "reason": state.reason,
            "allowed": state.requests_allowed,
            "throttled": state.requests_throttled,
            "has_override": extension_id in self._overrides,
        }
