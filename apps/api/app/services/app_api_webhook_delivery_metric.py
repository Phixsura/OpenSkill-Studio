"""App API Webhook Delivery Metric — track delivery performance metrics.

Manages delivery metrics:
- Record delivery latency per destination
- Track success/failure rates per destination
- Percentile calculations
- Per-installation scoped metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DestinationMetric:
    """Delivery metrics for a destination."""

    destination: str
    deliveries: int = 0
    successes: int = 0
    latencies: list[float] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        if self.deliveries == 0:
            return 100.0
        return round(self.successes / self.deliveries * 100, 1)

    @property
    def avg_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return round(sum(self.latencies) / len(self.latencies), 1)


class AppAPIWebhookDeliveryMetric:
    """Track delivery performance metrics."""

    def __init__(self, max_latencies: int = 500) -> None:
        self._max = max(1, max_latencies)
        self._metrics: dict[tuple[str, str], DestinationMetric] = {}

    def record(
        self, installation_id: str, destination: str,
        success: bool, latency_ms: float,
    ) -> DestinationMetric:
        if not installation_id:
            raise ValueError("installation_id is required")

        key = (installation_id, destination)
        if key not in self._metrics:
            self._metrics[key] = DestinationMetric(destination=destination)

        m = self._metrics[key]
        m.deliveries += 1
        if success:
            m.successes += 1
        m.latencies.append(latency_ms)
        if len(m.latencies) > self._max:
            m.latencies = m.latencies[-self._max:]
        return m

    def top_destinations(self, installation_id: str, limit: int = 10) -> list[DestinationMetric]:
        metrics = [m for (inst, _), m in self._metrics.items() if inst == installation_id]
        return sorted(metrics, key=lambda m: m.deliveries, reverse=True)[:limit]

    def slow_destinations(self, installation_id: str, threshold_ms: float = 1000) -> list[DestinationMetric]:
        return [m for (inst, _), m in self._metrics.items() if inst == installation_id and m.avg_latency > threshold_ms]
