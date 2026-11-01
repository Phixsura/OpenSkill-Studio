"""App API Developer Rate Limit Analytics — analyze rate limit patterns."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitAnalytics:
    consumer_id: str
    total_requests: int = 0
    throttled_requests: int = 0
    peak_rps: float = 0.0
    avg_rps: float = 0.0

    @property
    def throttle_rate(self) -> float:
        return round(self.throttled_requests / self.total_requests * 100, 1) if self.total_requests > 0 else 0.0

    @property
    def needs_upgrade(self) -> bool:
        return self.throttle_rate >= 5.0

class AppAPIDeveloperPlatformSDKApiDeveloperApiRateLimitAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[tuple[str, str], RateLimitAnalytics] = {}

    def record(self, installation_id: str, consumer_id: str, requests: int, throttled: int, peak_rps: float, avg_rps: float) -> RateLimitAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._analytics:
            self._analytics[key] = RateLimitAnalytics(consumer_id=consumer_id)
        a = self._analytics[key]
        a.total_requests += requests
        a.throttled_requests += throttled
        if peak_rps > a.peak_rps: a.peak_rps = peak_rps
        a.avg_rps = avg_rps
        return a

    def needs_upgrade(self, installation_id: str) -> list[RateLimitAnalytics]:
        return [a for (inst, _), a in self._analytics.items() if inst == installation_id and a.needs_upgrade]

    def most_throttled(self, installation_id: str, limit: int = 5) -> list[RateLimitAnalytics]:
        analytics = [a for (inst, _), a in self._analytics.items() if inst == installation_id]
        return sorted(analytics, key=lambda a: a.throttle_rate, reverse=True)[:limit]

    def all_analytics(self, installation_id: str) -> list[RateLimitAnalytics]:
        return [a for (inst, _), a in self._analytics.items() if inst == installation_id]
