"""App API Developer API Request Throttle — adaptive request throttling."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ThrottleState:
    consumer_id: str
    base_rate: int  # max requests per second
    current_rate: int
    backoff_factor: float = 1.0
    throttled_count: int = 0
    last_throttle_at: float = 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiRequestThrottle:
    def __init__(self) -> None:
        self._states: dict[tuple[str, str], ThrottleState] = {}

    def configure(self, installation_id: str, consumer_id: str, base_rate: int) -> ThrottleState:
        if not installation_id: raise ValueError("installation_id is required")
        if base_rate < 1: raise ValueError("base_rate must be >= 1")
        key = (installation_id, consumer_id)
        s = ThrottleState(consumer_id=consumer_id, base_rate=base_rate, current_rate=base_rate)
        self._states[key] = s
        return s

    def apply_backoff(self, installation_id: str, consumer_id: str) -> ThrottleState:
        s = self._get(installation_id, consumer_id)
        s.backoff_factor = min(s.backoff_factor * 2, 16.0)
        s.current_rate = max(1, int(s.base_rate / s.backoff_factor))
        s.throttled_count += 1
        s.last_throttle_at = time.time()
        return s

    def reset_backoff(self, installation_id: str, consumer_id: str) -> ThrottleState:
        s = self._get(installation_id, consumer_id)
        s.backoff_factor = 1.0
        s.current_rate = s.base_rate
        return s

    def is_throttled(self, installation_id: str, consumer_id: str) -> bool:
        s = self._states.get((installation_id, consumer_id))
        if s is None: return False
        return s.current_rate < s.base_rate

    def all_states(self, installation_id: str) -> list[ThrottleState]:
        return [s for (inst, _), s in self._states.items() if inst == installation_id]

    def throttled_consumers(self, installation_id: str) -> list[ThrottleState]:
        return [s for s in self.all_states(installation_id) if s.current_rate < s.base_rate]

    def _get(self, installation_id: str, consumer_id: str) -> ThrottleState:
        key = (installation_id, consumer_id)
        s = self._states.get(key)
        if s is None: raise KeyError(f"No throttle for {consumer_id}")
        return s
