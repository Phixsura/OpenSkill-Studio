"""Consumer API Rate Limit Analytics — analyze rate limiting patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitEvent:
    consumer_id: str
    endpoint: str
    allowed: bool
    timestamp: datetime
    remaining: int = 0
    limit: int = 0

@dataclass
class RateLimitAnalytics:
    consumer_id: str
    total_requests: int
    throttled_count: int
    throttle_rate_pct: float
    peak_hour: int  # 0-23
    most_throttled_endpoint: str
    avg_remaining_at_throttle: float

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiRateLimitAnalytics:
    def __init__(self) -> None:
        self._events: dict[tuple[str, str], list[RateLimitEvent]] = {}

    def record(self, installation_id: str, event: RateLimitEvent) -> RateLimitEvent:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, event.consumer_id)
        if key not in self._events:
            self._events[key] = []
        self._events[key].append(event)
        if len(self._events[key]) > 50000:
            self._events[key] = self._events[key][-50000:]
        return event

    def analyze(self, installation_id: str, consumer_id: str) -> RateLimitAnalytics:
        events = self._events.get((installation_id, consumer_id), [])
        if not events:
            return RateLimitAnalytics(consumer_id=consumer_id, total_requests=0, throttled_count=0, throttle_rate_pct=0, peak_hour=0, most_throttled_endpoint="", avg_remaining_at_throttle=0)
        throttled = [e for e in events if not e.allowed]
        throttle_rate = len(throttled) / len(events) * 100
        # Peak hour
        hour_counts: dict[int, int] = {}
        for e in events:
            h = e.timestamp.hour
            hour_counts[h] = hour_counts.get(h, 0) + 1
        peak_hour = max(hour_counts, key=hour_counts.get) if hour_counts else 0
        # Most throttled endpoint
        ep_throttle: dict[str, int] = {}
        for e in throttled:
            ep_throttle[e.endpoint] = ep_throttle.get(e.endpoint, 0) + 1
        most_throttled = max(ep_throttle, key=ep_throttle.get) if ep_throttle else ""
        # Avg remaining when throttled
        throttle_remaining = [e.remaining for e in throttled]
        avg_rem = sum(throttle_remaining) / len(throttle_remaining) if throttle_remaining else 0
        return RateLimitAnalytics(consumer_id=consumer_id, total_requests=len(events), throttled_count=len(throttled), throttle_rate_pct=round(throttle_rate, 1), peak_hour=peak_hour, most_throttled_endpoint=most_throttled, avg_remaining_at_throttle=round(avg_rem, 1))

    def get_events(self, installation_id: str, consumer_id: str, throttled_only: bool = False, limit: int = 50) -> list[RateLimitEvent]:
        events = self._events.get((installation_id, consumer_id), [])
        if throttled_only:
            events = [e for e in events if not e.allowed]
        return list(reversed(events[-limit:]))
