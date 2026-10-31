"""API Rate Tracker — track per-endpoint API usage with time series.

Records API call counts per endpoint per time window, enables
per-endpoint rate analysis, slowest endpoints, and usage patterns.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class EndpointStats:
    method: str
    path: str
    total_calls: int = 0
    total_errors: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        return round(self.total_latency_ms / max(1, self.total_calls), 2)

    @property
    def error_rate(self) -> float:
        return round(self.total_errors / max(1, self.total_calls) * 100, 2)


class APIRateTracker:
    """Tracks per-endpoint API usage metrics."""

    def __init__(self):
        self._stats: dict[str, dict[str, EndpointStats]] = defaultdict(dict)

    def _key(self, method: str, path: str) -> str:
        return f"{method}:{path}"

    def record(self, extension_id: str, method: str, path: str,
               latency_ms: float, status_code: int = 200) -> None:
        key = self._key(method, path)
        stats_map = self._stats[extension_id]
        if key not in stats_map:
            stats_map[key] = EndpointStats(method, path)
        s = stats_map[key]
        s.total_calls += 1
        s.total_latency_ms += latency_ms
        s.min_latency_ms = min(s.min_latency_ms, latency_ms)
        s.max_latency_ms = max(s.max_latency_ms, latency_ms)
        if status_code >= 400:
            s.total_errors += 1

    def get_endpoint_stats(self, extension_id: str, method: str, path: str) -> EndpointStats | None:
        return self._stats.get(extension_id, {}).get(self._key(method, path))

    def get_all_endpoints(self, extension_id: str) -> list[EndpointStats]:
        return sorted(self._stats.get(extension_id, {}).values(),
                      key=lambda s: s.total_calls, reverse=True)

    def get_slowest(self, extension_id: str, limit: int = 5) -> list[EndpointStats]:
        endpoints = list(self._stats.get(extension_id, {}).values())
        return sorted(endpoints, key=lambda s: s.avg_latency_ms, reverse=True)[:limit]

    def get_most_errors(self, extension_id: str, limit: int = 5) -> list[EndpointStats]:
        endpoints = list(self._stats.get(extension_id, {}).values())
        return sorted(endpoints, key=lambda s: s.error_rate, reverse=True)[:limit]

    def get_summary(self, extension_id: str) -> dict:
        endpoints = self._stats.get(extension_id, {}).values()
        if not endpoints:
            return {"extension_id": extension_id, "endpoints": 0, "total_calls": 0}
        total_calls = sum(s.total_calls for s in endpoints)
        total_errors = sum(s.total_errors for s in endpoints)
        return {
            "extension_id": extension_id,
            "endpoints": len(endpoints),
            "total_calls": total_calls,
            "total_errors": total_errors,
            "overall_error_rate": round(total_errors / max(1, total_calls) * 100, 2),
            "avg_latency_ms": round(sum(s.total_latency_ms for s in endpoints) / max(1, total_calls), 2),
        }
