"""App API Webhook Stats — aggregate webhook delivery statistics.

Manages webhook statistics:
- Track delivery counts by status
- Calculate delivery latency stats
- Failure rate trending
- Per-installation scoped stats
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class WebhookStats:
    """Aggregated webhook delivery statistics."""

    total_sent: int = 0
    total_failed: int = 0
    total_retried: int = 0
    latencies: list[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        total = self.total_sent + self.total_failed
        if total == 0:
            return 100.0
        return round(self.total_sent / total * 100, 1)

    @property
    def avg_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return round(sum(self.latencies) / len(self.latencies), 1)

    @property
    def p95_latency(self) -> float:
        if not self.latencies:
            return 0.0
        sorted_l = sorted(self.latencies)
        idx = int(len(sorted_l) * 0.95)
        return sorted_l[min(idx, len(sorted_l) - 1)]


class AppAPIWebhookStats:
    """Aggregate webhook delivery statistics."""

    def __init__(self, max_latencies: int = 1000) -> None:
        self._max = max(1, max_latencies)
        self._stats: dict[str, WebhookStats] = {}

    def record_delivery(
        self, installation_id: str, success: bool, latency_ms: float, retried: bool = False,
    ) -> WebhookStats:
        if not installation_id:
            raise ValueError("installation_id is required")

        stats = self._stats.setdefault(installation_id, WebhookStats())
        if success:
            stats.total_sent += 1
        else:
            stats.total_failed += 1
        if retried:
            stats.total_retried += 1
        stats.latencies.append(latency_ms)
        if len(stats.latencies) > self._max:
            stats.latencies = stats.latencies[-self._max:]
        return stats

    def get_stats(self, installation_id: str) -> WebhookStats:
        return self._stats.get(installation_id, WebhookStats())

    def reset(self, installation_id: str) -> None:
        self._stats[installation_id] = WebhookStats()
