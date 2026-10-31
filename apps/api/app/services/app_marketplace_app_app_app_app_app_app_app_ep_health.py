"""API endpoint health checker — check individual endpoint health."""
from __future__ import annotations
from collections import defaultdict


class EndpointHealthChecker:
    def __init__(self):
        self._metrics: dict[str, dict] = defaultdict(lambda: {"total": 0, "errors": 0, "total_ms": 0})

    def record(self, endpoint: str, status: int, latency_ms: float) -> dict:
        m = self._metrics[endpoint]
        m["total"] += 1
        m["total_ms"] += latency_ms
        if status >= 500:
            m["errors"] += 1
        return {"endpoint": endpoint, "recorded": True}

    def health(self, endpoint: str) -> dict:
        m = self._metrics.get(endpoint, {"total": 0, "errors": 0, "total_ms": 0})
        if m["total"] == 0:
            return {"endpoint": endpoint, "status": "no_data"}
        error_rate = round(m["errors"] / m["total"] * 100, 2)
        avg_ms = round(m["total_ms"] / m["total"], 1)
        status = "healthy" if error_rate < 1 and avg_ms < 500 else ("degraded" if error_rate < 5 else "unhealthy")
        return {"endpoint": endpoint, "status": status, "error_rate": error_rate,
                "avg_ms": avg_ms, "total_requests": m["total"]}

    def all_endpoints(self) -> list[dict]:
        return [self.health(ep) for ep in sorted(self._metrics.keys())]
