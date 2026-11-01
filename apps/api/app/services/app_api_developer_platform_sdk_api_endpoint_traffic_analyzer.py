"""App API Developer Endpoint Traffic Analyzer — analyze traffic patterns per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointTraffic:
    endpoint: str
    method: str
    total_requests: int = 0
    unique_consumers: int = 0
    avg_payload_bytes: int = 0
    peak_rps: float = 0.0

    @property
    def traffic_tier(self) -> str:
        if self.total_requests >= 1000000: return "mega"
        if self.total_requests >= 100000: return "high"
        if self.total_requests >= 10000: return "medium"
        return "low"

class AppAPIDeveloperPlatformSDKApiEndpointTrafficAnalyzer:
    def __init__(self) -> None:
        self._traffic: dict[tuple[str, str, str], EndpointTraffic] = {}

    def record(self, installation_id: str, endpoint: str, method: str, requests: int, unique_consumers: int, avg_payload_bytes: int = 0, peak_rps: float = 0.0) -> EndpointTraffic:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        if key not in self._traffic:
            self._traffic[key] = EndpointTraffic(endpoint=endpoint, method=method.upper())
        t = self._traffic[key]
        t.total_requests += requests
        t.unique_consumers = max(t.unique_consumers, unique_consumers)
        t.avg_payload_bytes = avg_payload_bytes
        if peak_rps > t.peak_rps: t.peak_rps = peak_rps
        return t

    def hottest(self, installation_id: str, limit: int = 5) -> list[EndpointTraffic]:
        traffic = [t for (inst, _, _), t in self._traffic.items() if inst == installation_id]
        return sorted(traffic, key=lambda t: t.total_requests, reverse=True)[:limit]

    def by_tier(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _, _), t in self._traffic.items():
            if inst == installation_id: counts[t.traffic_tier] = counts.get(t.traffic_tier, 0) + 1
        return counts

    def all_traffic(self, installation_id: str) -> list[EndpointTraffic]:
        return [t for (inst, _, _), t in self._traffic.items() if inst == installation_id]
