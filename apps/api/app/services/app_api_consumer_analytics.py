"""App API Consumer Analytics — per-consumer usage analytics."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerAnalytics:
    consumer_id: str
    total_requests: int = 0
    error_count: int = 0
    avg_latency_ms: float = 0.0
    top_endpoints: list[str] = field(default_factory=list)
    last_active: str = ""

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.error_count / self.total_requests * 100, 1)

class AppAPIConsumerAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[tuple[str, str], ConsumerAnalytics] = {}

    def record(self, installation_id: str, consumer_id: str, endpoint: str, latency_ms: float, success: bool, day: str = "") -> ConsumerAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._analytics:
            self._analytics[key] = ConsumerAnalytics(consumer_id=consumer_id)
        a = self._analytics[key]
        a.total_requests += 1
        if not success: a.error_count += 1
        # Running average
        a.avg_latency_ms = round(((a.avg_latency_ms * (a.total_requests - 1)) + latency_ms) / a.total_requests, 1)
        if endpoint not in a.top_endpoints: a.top_endpoints.append(endpoint)
        if day: a.last_active = day
        return a

    def get(self, installation_id: str, consumer_id: str) -> ConsumerAnalytics:
        a = self._analytics.get((installation_id, consumer_id))
        if a is None: raise KeyError(f"No analytics for {consumer_id}")
        return a

    def top_consumers(self, installation_id: str, limit: int = 10) -> list[ConsumerAnalytics]:
        consumers = [a for (inst, _), a in self._analytics.items() if inst == installation_id]
        return sorted(consumers, key=lambda a: a.total_requests, reverse=True)[:limit]

    def high_error_consumers(self, installation_id: str, threshold: float = 5.0) -> list[ConsumerAnalytics]:
        return [a for (inst, _), a in self._analytics.items() if inst == installation_id and a.error_rate > threshold]
