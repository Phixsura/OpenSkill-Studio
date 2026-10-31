"""API Latency Percentile — track and compute latency percentiles per endpoint."""
from __future__ import annotations
from dataclasses import dataclass, field
import bisect
import structlog

log = structlog.get_logger()

@dataclass
class LatencyBucket:
    endpoint: str
    method: str
    samples: list[float] = field(default_factory=list)

    def add(self, latency_ms: float) -> None:
        bisect.insort(self.samples, latency_ms)

    def percentile(self, p: float) -> float:
        if not self.samples: return 0.0
        if not 0 <= p <= 100: raise ValueError("Percentile must be 0-100")
        idx = int(len(self.samples) * p / 100)
        idx = min(idx, len(self.samples) - 1)
        return self.samples[idx]

    @property
    def p50(self) -> float: return self.percentile(50)
    @property
    def p95(self) -> float: return self.percentile(95)
    @property
    def p99(self) -> float: return self.percentile(99)
    @property
    def avg(self) -> float: return round(sum(self.samples) / len(self.samples), 2) if self.samples else 0.0
    @property
    def count(self) -> int: return len(self.samples)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiLatencyPercentile:
    def __init__(self, max_samples: int = 10000) -> None:
        self._buckets: dict[tuple[str, str, str], LatencyBucket] = {}
        self._max = max(100, max_samples)

    def record(self, installation_id: str, endpoint: str, method: str, latency_ms: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if latency_ms < 0: raise ValueError("latency must be non-negative")
        key = (installation_id, method.upper(), endpoint)
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = LatencyBucket(endpoint=endpoint, method=method.upper())
            self._buckets[key] = bucket
        bucket.add(latency_ms)
        if len(bucket.samples) > self._max:
            bucket.samples = bucket.samples[-self._max:]

    def get_percentiles(self, installation_id: str, endpoint: str, method: str) -> dict[str, float]:
        bucket = self._buckets.get((installation_id, method.upper(), endpoint))
        if bucket is None: return {"p50": 0, "p95": 0, "p99": 0, "avg": 0, "count": 0}
        return {"p50": bucket.p50, "p95": bucket.p95, "p99": bucket.p99, "avg": bucket.avg, "count": bucket.count}

    def slow_endpoints(self, installation_id: str, p99_threshold_ms: float = 1000) -> list[dict[str, object]]:
        results = []
        for (inst, method, ep), bucket in self._buckets.items():
            if inst != installation_id: continue
            if bucket.p99 > p99_threshold_ms:
                results.append({"endpoint": ep, "method": method, "p99": bucket.p99, "count": bucket.count})
        return results

    def list_endpoints(self, installation_id: str) -> list[str]:
        return list({ep for (inst, _, ep) in self._buckets if inst == installation_id})
