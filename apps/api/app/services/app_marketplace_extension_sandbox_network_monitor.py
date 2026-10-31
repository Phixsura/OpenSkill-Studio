"""Sandbox Network Monitor — track and analyze network activity in sandboxes.

Monitors HTTP requests made by extensions, tracks bandwidth, latency
distributions, endpoint frequency, and detects anomalous patterns.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class RequestMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class NetworkRequest:
    request_id: str
    sandbox_id: str
    method: RequestMethod
    url: str
    status_code: int
    request_bytes: int
    response_bytes: int
    latency_ms: float
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class SandboxNetworkMonitorService:
    """Monitors and analyzes sandbox network activity."""

    BANDWIDTH_LIMIT_MB = 100
    REQUEST_RATE_LIMIT = 1000  # per minute

    def __init__(self):
        self._requests: dict[str, list[NetworkRequest]] = defaultdict(list)

    def record(self, sandbox_id: str, method: RequestMethod, url: str,
               status_code: int, request_bytes: int = 0,
               response_bytes: int = 0, latency_ms: float = 0) -> NetworkRequest:
        req = NetworkRequest(
            request_id=f"nr_{secrets.token_urlsafe(8)}",
            sandbox_id=sandbox_id, method=method, url=url,
            status_code=status_code, request_bytes=request_bytes,
            response_bytes=response_bytes, latency_ms=latency_ms,
        )
        self._requests[sandbox_id].append(req)
        return req

    def get_bandwidth(self, sandbox_id: str) -> dict:
        reqs = self._requests.get(sandbox_id, [])
        total_in = sum(r.request_bytes for r in reqs)
        total_out = sum(r.response_bytes for r in reqs)
        total_mb = (total_in + total_out) / (1024 * 1024)
        return {
            "request_bytes": total_in, "response_bytes": total_out,
            "total_mb": round(total_mb, 2),
            "limit_mb": self.BANDWIDTH_LIMIT_MB,
            "usage_percent": round(total_mb / self.BANDWIDTH_LIMIT_MB * 100, 1),
        }

    def get_latency_stats(self, sandbox_id: str) -> dict:
        reqs = self._requests.get(sandbox_id, [])
        if not reqs:
            return {"count": 0, "avg": 0, "p50": 0, "p95": 0, "p99": 0, "max": 0}
        latencies = sorted(r.latency_ms for r in reqs)
        n = len(latencies)
        return {
            "count": n,
            "avg": round(sum(latencies) / n, 1),
            "p50": latencies[n // 2],
            "p95": latencies[int(n * 0.95)],
            "p99": latencies[int(n * 0.99)],
            "max": latencies[-1],
        }

    def get_top_endpoints(self, sandbox_id: str, limit: int = 10) -> list[dict]:
        freq: dict[str, int] = defaultdict(int)
        for r in self._requests.get(sandbox_id, []):
            freq[r.url] += 1
        sorted_eps = sorted(freq.items(), key=lambda x: -x[1])
        return [{"url": url, "count": count} for url, count in sorted_eps[:limit]]

    def get_error_rate(self, sandbox_id: str) -> float:
        reqs = self._requests.get(sandbox_id, [])
        if not reqs:
            return 0.0
        errors = sum(1 for r in reqs if r.status_code >= 400)
        return round(errors / len(reqs) * 100, 1)

    def detect_anomalies(self, sandbox_id: str) -> list[str]:
        anomalies = []
        reqs = self._requests.get(sandbox_id, [])
        if not reqs:
            return anomalies

        bw = self.get_bandwidth(sandbox_id)
        if bw["usage_percent"] > 80:
            anomalies.append(f"High bandwidth usage: {bw['total_mb']}MB ({bw['usage_percent']}%)")

        error_rate = self.get_error_rate(sandbox_id)
        if error_rate > 50:
            anomalies.append(f"High error rate: {error_rate}%")

        latency = self.get_latency_stats(sandbox_id)
        if latency["p95"] > 5000:
            anomalies.append(f"High p95 latency: {latency['p95']}ms")

        return anomalies

    def get_summary(self, sandbox_id: str) -> dict:
        reqs = self._requests.get(sandbox_id, [])
        by_method: dict[str, int] = defaultdict(int)
        for r in reqs:
            by_method[r.method.value] += 1
        return {
            "total_requests": len(reqs),
            "by_method": dict(by_method),
            "error_rate": self.get_error_rate(sandbox_id),
            "bandwidth": self.get_bandwidth(sandbox_id),
            "latency": self.get_latency_stats(sandbox_id),
        }
