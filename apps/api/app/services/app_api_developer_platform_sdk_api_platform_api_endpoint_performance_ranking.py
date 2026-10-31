"""App API Developer Endpoint Performance Ranking — rank endpoints by performance."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointPerformance:
    endpoint: str
    avg_latency_ms: float
    p99_latency_ms: float
    error_rate_pct: float
    requests_per_day: int

    @property
    def performance_score(self) -> int:
        s = 100
        if self.avg_latency_ms > 200: s -= 20
        if self.p99_latency_ms > 1000: s -= 25
        if self.error_rate_pct > 1: s -= 20
        if self.error_rate_pct > 5: s -= 15
        if self.requests_per_day < 100: s -= 10
        return max(0, s)

    @property
    def rank_label(self) -> str:
        s = self.performance_score
        if s >= 90: return "⚡ Fast"
        if s >= 70: return "✅ Good"
        if s >= 50: return "⚠️ Slow"
        return "🐌 Poor"

class AppAPIDeveloperPlatformSDKApiPlatformApiEndpointPerformanceRanking:
    def __init__(self) -> None:
        self._endpoints: dict[tuple[str, str], EndpointPerformance] = {}

    def record(self, installation_id: str, endpoint: str, avg_latency_ms: float, p99_latency_ms: float, error_rate_pct: float, requests_per_day: int) -> EndpointPerformance:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        e = EndpointPerformance(endpoint=endpoint, avg_latency_ms=avg_latency_ms, p99_latency_ms=p99_latency_ms, error_rate_pct=error_rate_pct, requests_per_day=requests_per_day)
        self._endpoints[key] = e
        return e

    def ranked(self, installation_id: str) -> list[EndpointPerformance]:
        endpoints = [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
        return sorted(endpoints, key=lambda e: e.performance_score, reverse=True)

    def slowest(self, installation_id: str, limit: int = 5) -> list[EndpointPerformance]:
        return list(reversed(self.ranked(installation_id)))[:limit]

    def all_endpoints(self, installation_id: str) -> list[EndpointPerformance]:
        return [e for (inst, _), e in self._endpoints.items() if inst == installation_id]
