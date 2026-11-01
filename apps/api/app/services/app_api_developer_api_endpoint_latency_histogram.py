"""App API Developer Endpoint Latency Histogram — latency distribution per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

BUCKETS = [10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]

@dataclass
class LatencyHistogram:
    endpoint: str
    buckets: dict[int, int] = field(default_factory=lambda: {b: 0 for b in BUCKETS})
    total: int = 0
    sum_ms: float = 0.0

    @property
    def avg_ms(self) -> float:
        return round(self.sum_ms / self.total, 2) if self.total > 0 else 0.0

    @property
    def p99_bucket(self) -> int:
        if self.total == 0: return 0
        threshold = self.total * 0.99
        cumulative = 0
        for b in sorted(self.buckets.keys()):
            cumulative += self.buckets[b]
            if cumulative >= threshold: return b
        return max(self.buckets.keys())

class AppAPIDeveloperAPIEndpointLatencyHistogram:
    def __init__(self) -> None:
        self._histograms: dict[tuple[str, str], LatencyHistogram] = {}

    def record(self, installation_id: str, endpoint: str, latency_ms: float) -> LatencyHistogram:
        if not installation_id: raise ValueError("installation_id is required")
        if latency_ms < 0: raise ValueError("latency_ms must be non-negative")
        key = (installation_id, endpoint)
        if key not in self._histograms:
            self._histograms[key] = LatencyHistogram(endpoint=endpoint)
        h = self._histograms[key]
        h.total += 1
        h.sum_ms += latency_ms
        for b in sorted(BUCKETS):
            if latency_ms <= b:
                h.buckets[b] += 1
                break
        else:
            h.buckets[BUCKETS[-1]] += 1
        return h

    def get(self, installation_id: str, endpoint: str) -> LatencyHistogram | None:
        return self._histograms.get((installation_id, endpoint))

    def slowest(self, installation_id: str, limit: int = 5) -> list[LatencyHistogram]:
        hists = [h for (inst, _), h in self._histograms.items() if inst == installation_id]
        return sorted(hists, key=lambda h: h.avg_ms, reverse=True)[:limit]
