"""Consumer API Latency Tracker — track per-consumer request latency distributions."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class LatencyBucket:
    range_label: str  # "<50ms", "50-100ms", "100-500ms", "500ms-1s", ">1s"
    count: int = 0

@dataclass
class LatencyDistribution:
    consumer_id: str
    total_requests: int
    p50_ms: float
    p95_ms: float
    p99_ms: float
    avg_ms: float
    buckets: list[LatencyBucket] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerApiApiConsumerApiApiLatencyTracker:
    def __init__(self) -> None:
        self._latencies: dict[tuple[str, str], list[float]] = {}

    def record(self, installation_id: str, consumer_id: str, latency_ms: float) -> None:
        if not installation_id:
            raise ValueError("installation_id is required")
        if latency_ms < 0:
            raise ValueError("latency must be non-negative")
        key = (installation_id, consumer_id)
        if key not in self._latencies:
            self._latencies[key] = []
        self._latencies[key].append(latency_ms)
        if len(self._latencies[key]) > 100000:
            self._latencies[key] = self._latencies[key][-100000:]

    def get_distribution(self, installation_id: str, consumer_id: str) -> LatencyDistribution:
        values = self._latencies.get((installation_id, consumer_id), [])
        if not values:
            return LatencyDistribution(consumer_id=consumer_id, total_requests=0, p50_ms=0, p95_ms=0, p99_ms=0, avg_ms=0)
        sorted_v = sorted(values)
        n = len(sorted_v)
        p50 = sorted_v[int(n * 0.5)]
        p95 = sorted_v[min(int(n * 0.95), n - 1)]
        p99 = sorted_v[min(int(n * 0.99), n - 1)]
        avg = sum(values) / n
        # Buckets
        bucket_ranges = [("<50ms", 0, 50), ("50-100ms", 50, 100), ("100-500ms", 100, 500), ("500ms-1s", 500, 1000), (">1s", 1000, float("inf"))]
        buckets = []
        for label, low, high in bucket_ranges:
            count = sum(1 for v in values if low <= v < high)
            buckets.append(LatencyBucket(range_label=label, count=count))
        return LatencyDistribution(consumer_id=consumer_id, total_requests=n, p50_ms=round(p50, 1), p95_ms=round(p95, 1), p99_ms=round(p99, 1), avg_ms=round(avg, 1), buckets=buckets)
