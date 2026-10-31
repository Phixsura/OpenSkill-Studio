"""App API Developer Webhook Throttle Manager — per-destination delivery throttling."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ThrottleConfig:
    destination: str
    max_per_second: int
    max_per_minute: int
    current_second_count: int = 0
    current_minute_count: int = 0
    throttled_count: int = 0
    last_reset_second: float = field(default_factory=time.time)
    last_reset_minute: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiWebhookThrottleManager:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], ThrottleConfig] = {}

    def configure(self, installation_id: str, destination: str, max_per_second: int, max_per_minute: int) -> ThrottleConfig:
        if not installation_id: raise ValueError("installation_id is required")
        if max_per_second < 1: raise ValueError("max_per_second must be >= 1")
        if max_per_minute < max_per_second: raise ValueError("max_per_minute must be >= max_per_second")
        key = (installation_id, destination)
        c = ThrottleConfig(destination=destination, max_per_second=max_per_second, max_per_minute=max_per_minute)
        self._configs[key] = c
        return c

    def try_deliver(self, installation_id: str, destination: str) -> bool:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: return True  # no throttle configured
        now = time.time()
        if now - c.last_reset_second >= 1.0:
            c.current_second_count = 0
            c.last_reset_second = now
        if now - c.last_reset_minute >= 60.0:
            c.current_minute_count = 0
            c.last_reset_minute = now
        if c.current_second_count >= c.max_per_second or c.current_minute_count >= c.max_per_minute:
            c.throttled_count += 1
            return False
        c.current_second_count += 1
        c.current_minute_count += 1
        return True

    def stats(self, installation_id: str, destination: str) -> dict[str, int]:
        key = (installation_id, destination)
        c = self._configs.get(key)
        if c is None: return {"throttled": 0}
        return {"throttled": c.throttled_count, "second_count": c.current_second_count, "minute_count": c.current_minute_count}

    def all_configs(self, installation_id: str) -> list[ThrottleConfig]:
        return [c for (inst, _), c in self._configs.items() if inst == installation_id]
