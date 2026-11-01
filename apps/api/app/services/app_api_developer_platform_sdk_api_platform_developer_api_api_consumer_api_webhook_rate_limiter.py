"""API Consumer Webhook Rate Limiter — per-consumer webhook delivery rate limiting."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class WebhookRateLimit:
    consumer_id: str
    max_per_second: int = 10
    max_per_minute: int = 100
    current_second: int = 0
    current_minute: int = 0
    total_limited: int = 0
    last_reset_s: float = field(default_factory=time.time)
    last_reset_m: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookRateLimiter:
    def __init__(self) -> None:
        self._limits: dict[tuple[str, str], WebhookRateLimit] = {}

    def configure(self, installation_id: str, consumer_id: str, max_per_second: int = 10, max_per_minute: int = 100) -> WebhookRateLimit:
        if not installation_id: raise ValueError("installation_id is required")
        if max_per_second < 1: raise ValueError("max_per_second must be >= 1")
        if max_per_minute < max_per_second: raise ValueError("max_per_minute must be >= max_per_second")
        rl = WebhookRateLimit(consumer_id=consumer_id, max_per_second=max_per_second, max_per_minute=max_per_minute)
        self._limits[(installation_id, consumer_id)] = rl
        return rl

    def allow(self, installation_id: str, consumer_id: str) -> bool:
        rl = self._limits.get((installation_id, consumer_id))
        if rl is None: return True
        now = time.time()
        if now - rl.last_reset_s >= 1: rl.current_second = 0; rl.last_reset_s = now
        if now - rl.last_reset_m >= 60: rl.current_minute = 0; rl.last_reset_m = now
        if rl.current_second >= rl.max_per_second or rl.current_minute >= rl.max_per_minute:
            rl.total_limited += 1
            return False
        rl.current_second += 1
        rl.current_minute += 1
        return True

    def get_limit(self, installation_id: str, consumer_id: str) -> WebhookRateLimit | None:
        return self._limits.get((installation_id, consumer_id))

    def list_limits(self, installation_id: str) -> list[WebhookRateLimit]:
        return [rl for (inst, _), rl in self._limits.items() if inst == installation_id]
