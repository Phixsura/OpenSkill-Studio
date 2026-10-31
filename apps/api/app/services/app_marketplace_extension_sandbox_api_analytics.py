"""Sandbox API Analytics — real-time analytics for extension API usage.

Tracks endpoint hits, response times, error rates, top consumers,
and generates usage reports with trend detection.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class EndpointStats:
    endpoint: str
    method: str
    hits: int = 0
    total_latency_ms: float = 0.0
    errors: int = 0
    last_hit: float = 0.0

    @property
    def avg_latency(self) -> float:
        return round(self.total_latency_ms / max(self.hits, 1), 1)

    @property
    def error_rate(self) -> float:
        return round(self.errors / max(self.hits, 1) * 100, 1)


class SandboxApiAnalyticsService:
    """Real-time API usage analytics for extensions."""

    def __init__(self):
        self._stats: dict[str, dict[str, EndpointStats]] = defaultdict(dict)
        self._consumers: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def record(self, sandbox_id: str, method: str, endpoint: str,
               latency_ms: float, status_code: int,
               consumer: str = "") -> None:
        key = f"{method}:{endpoint}"
        stats = self._stats[sandbox_id]
        if key not in stats:
            stats[key] = EndpointStats(endpoint=endpoint, method=method)
        s = stats[key]
        s.hits += 1
        s.total_latency_ms += latency_ms
        s.last_hit = time.time()
        if status_code >= 400:
            s.errors += 1
        if consumer:
            self._consumers[sandbox_id][consumer] += 1

    def get_top_endpoints(self, sandbox_id: str, limit: int = 10) -> list[dict]:
        stats = self._stats.get(sandbox_id, {})
        sorted_eps = sorted(stats.values(), key=lambda s: s.hits, reverse=True)
        return [{"method": s.method, "endpoint": s.endpoint, "hits": s.hits,
                 "avg_latency": s.avg_latency, "error_rate": s.error_rate}
                for s in sorted_eps[:limit]]

    def get_slowest(self, sandbox_id: str, limit: int = 10) -> list[dict]:
        stats = self._stats.get(sandbox_id, {})
        sorted_eps = sorted(stats.values(), key=lambda s: s.avg_latency, reverse=True)
        return [{"method": s.method, "endpoint": s.endpoint,
                 "avg_latency": s.avg_latency, "hits": s.hits}
                for s in sorted_eps[:limit]]

    def get_error_prone(self, sandbox_id: str, limit: int = 10) -> list[dict]:
        stats = self._stats.get(sandbox_id, {})
        error_eps = [s for s in stats.values() if s.errors > 0]
        sorted_eps = sorted(error_eps, key=lambda s: s.error_rate, reverse=True)
        return [{"method": s.method, "endpoint": s.endpoint,
                 "error_rate": s.error_rate, "errors": s.errors}
                for s in sorted_eps[:limit]]

    def get_top_consumers(self, sandbox_id: str, limit: int = 10) -> list[dict]:
        consumers = self._consumers.get(sandbox_id, {})
        sorted_c = sorted(consumers.items(), key=lambda x: -x[1])
        return [{"consumer": c, "requests": n} for c, n in sorted_c[:limit]]

    def get_summary(self, sandbox_id: str) -> dict:
        stats = self._stats.get(sandbox_id, {})
        total_hits = sum(s.hits for s in stats.values())
        total_errors = sum(s.errors for s in stats.values())
        all_latencies = [s.avg_latency for s in stats.values() if s.hits > 0]
        return {
            "total_endpoints": len(stats),
            "total_hits": total_hits,
            "total_errors": total_errors,
            "overall_error_rate": round(total_errors / max(total_hits, 1) * 100, 1),
            "avg_latency": round(sum(all_latencies) / max(len(all_latencies), 1), 1),
        }
