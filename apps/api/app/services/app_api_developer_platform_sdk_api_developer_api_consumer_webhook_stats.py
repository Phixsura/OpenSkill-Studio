"""App API Developer Consumer Webhook Stats — aggregate webhook stats per consumer."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerWebhookStats:
    consumer_id: str
    destinations: int = 0
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    avg_latency_ms: float = 0.0
    retries: int = 0

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def retry_rate(self) -> float:
        return round(self.retries / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 0.0

    @property
    def health_status(self) -> str:
        r = self.success_rate
        if r >= 99: return "excellent"
        if r >= 95: return "good"
        if r >= 90: return "fair"
        return "poor"

class AppAPIDeveloperPlatformSDKApiDeveloperApiConsumerWebhookStats:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str], ConsumerWebhookStats] = {}

    def update(self, installation_id: str, consumer_id: str, **kwargs) -> ConsumerWebhookStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        s = ConsumerWebhookStats(consumer_id=consumer_id)
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._stats[key] = s
        return s

    def poorest(self, installation_id: str, limit: int = 5) -> list[ConsumerWebhookStats]:
        stats = [s for (inst, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: s.success_rate)[:limit]

    def by_health(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), s in self._stats.items():
            if inst == installation_id: counts[s.health_status] = counts.get(s.health_status, 0) + 1
        return counts

    def all_stats(self, installation_id: str) -> list[ConsumerWebhookStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id]
