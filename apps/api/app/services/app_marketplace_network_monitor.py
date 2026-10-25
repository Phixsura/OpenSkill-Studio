"""Network Monitor — track outbound network calls from sandboxed extensions.

Records all network requests made by extensions, tracks latency,
bandwidth, and provides analytics on network usage patterns.
"""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class NetworkRequest:
    request_id: str
    extension_id: str
    method: str
    url: str
    status_code: int = 0
    request_bytes: int = 0
    response_bytes: int = 0
    latency_ms: float = 0.0
    timestamp: str = ""
    blocked: bool = False
    block_reason: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class NetworkMonitor:
    """Monitors outbound network requests from sandboxed extensions."""

    def __init__(self, bandwidth_limit_mb: float = 100.0):
        self._requests: dict[str, list[NetworkRequest]] = defaultdict(list)
        self._bandwidth_limit = bandwidth_limit_mb * 1024 * 1024

    def record(self, request: NetworkRequest) -> None:
        self._requests[request.extension_id].append(request)

    def get_requests(self, extension_id: str, method: str | None = None,
                     blocked_only: bool = False, limit: int = 100) -> list[NetworkRequest]:
        reqs = self._requests.get(extension_id, [])
        if method:
            reqs = [r for r in reqs if r.method == method]
        if blocked_only:
            reqs = [r for r in reqs if r.blocked]
        return reqs[-limit:]

    def get_bandwidth_used(self, extension_id: str) -> dict:
        reqs = self._requests.get(extension_id, [])
        sent = sum(r.request_bytes for r in reqs)
        received = sum(r.response_bytes for r in reqs)
        total = sent + received
        return {
            "extension_id": extension_id,
            "sent_bytes": sent, "received_bytes": received,
            "total_bytes": total, "total_mb": round(total / 1024 / 1024, 2),
            "limit_mb": round(self._bandwidth_limit / 1024 / 1024, 2),
            "percent_used": round(total / max(1, self._bandwidth_limit) * 100, 1),
            "exceeded": total > self._bandwidth_limit,
        }

    def get_top_domains(self, extension_id: str, limit: int = 10) -> list[dict]:
        reqs = self._requests.get(extension_id, [])
        domain_stats: dict[str, dict] = {}
        for r in reqs:
            # Extract domain from URL
            domain = r.url.split("//")[-1].split("/")[0].split(":")[0] if "//" in r.url else r.url
            if domain not in domain_stats:
                domain_stats[domain] = {"domain": domain, "count": 0, "total_bytes": 0, "avg_latency": 0, "latencies": []}
            domain_stats[domain]["count"] += 1
            domain_stats[domain]["total_bytes"] += r.response_bytes
            domain_stats[domain]["latencies"].append(r.latency_ms)

        for d in domain_stats.values():
            lats = d.pop("latencies")
            d["avg_latency"] = round(sum(lats) / len(lats), 1) if lats else 0

        return sorted(domain_stats.values(), key=lambda d: d["count"], reverse=True)[:limit]

    def get_error_rate(self, extension_id: str) -> float:
        reqs = self._requests.get(extension_id, [])
        if not reqs:
            return 0.0
        errors = sum(1 for r in reqs if r.status_code >= 400 or r.blocked)
        return round(errors / len(reqs) * 100, 2)

    def get_summary(self, extension_id: str) -> dict:
        reqs = self._requests.get(extension_id, [])
        return {
            "extension_id": extension_id,
            "total_requests": len(reqs),
            "blocked_requests": sum(1 for r in reqs if r.blocked),
            "error_rate": self.get_error_rate(extension_id),
            "bandwidth": self.get_bandwidth_used(extension_id),
            "unique_domains": len(set(
                r.url.split("//")[-1].split("/")[0] for r in reqs if "//" in r.url
            )),
        }
