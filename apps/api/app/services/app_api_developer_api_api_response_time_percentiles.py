"""App API Developer API Response Time Percentiles — p50/p90/p95/p99 tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
import bisect
import structlog

log = structlog.get_logger()

@dataclass
class Percentiles:
    endpoint: str
    p50: float = 0.0
    p90: float = 0.0
    p95: float = 0.0
    p99: float = 0.0
    count: int = 0

class AppAPIDeveloperAPIApiResponseTimePercentiles:
    def __init__(self) -> None:
        self._samples: dict[tuple[str, str], list[float]] = {}

    def record(self, installation_id: str, endpoint: str, latency_ms: float) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        if latency_ms < 0: raise ValueError("latency must be non-negative")
        key = (installation_id, endpoint)
        samples = self._samples.setdefault(key, [])
        bisect.insort(samples, latency_ms)

    def calculate(self, installation_id: str, endpoint: str) -> Percentiles:
        key = (installation_id, endpoint)
        samples = self._samples.get(key, [])
        if not samples:
            return Percentiles(endpoint=endpoint)
        n = len(samples)
        return Percentiles(
            endpoint=endpoint,
            p50=samples[int(n * 0.5)],
            p90=samples[int(n * 0.9)],
            p95=samples[min(int(n * 0.95), n - 1)],
            p99=samples[min(int(n * 0.99), n - 1)],
            count=n,
        )

    def all_endpoints(self, installation_id: str) -> list[Percentiles]:
        endpoints = set(ep for (inst, ep) in self._samples if inst == installation_id)
        return [self.calculate(installation_id, ep) for ep in sorted(endpoints)]

    def slowest_p99(self, installation_id: str, limit: int = 5) -> list[Percentiles]:
        all_p = self.all_endpoints(installation_id)
        return sorted(all_p, key=lambda p: p.p99, reverse=True)[:limit]
