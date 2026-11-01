"""API Endpoint Analytics — per-endpoint analytics with top consumers and error rates."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class EndpointMetrics:
    endpoint: str
    method: str
    total_requests: int = 0
    success_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    consumers: dict[str, int] = field(default_factory=dict)

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round((self.error_count / self.total_requests) * 100, 2)

    @property
    def avg_latency(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.total_latency_ms / self.total_requests, 2)

    @property
    def top_consumers(self) -> list[tuple[str, int]]:
        return sorted(self.consumers.items(), key=lambda x: -x[1])[:5]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiEndpointAnalytics:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str, str], EndpointMetrics] = {}

    def record(self, installation_id: str, method: str, endpoint: str, consumer_id: str, status_code: int, latency_ms: float) -> EndpointMetrics:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, method.upper(), endpoint)
        m = self._metrics.get(key)
        if m is None:
            m = EndpointMetrics(endpoint=endpoint, method=method.upper())
            self._metrics[key] = m
        m.total_requests += 1
        m.total_latency_ms += latency_ms
        if 200 <= status_code < 400: m.success_count += 1
        else: m.error_count += 1
        m.consumers[consumer_id] = m.consumers.get(consumer_id, 0) + 1
        return m

    def get_metrics(self, installation_id: str, method: str, endpoint: str) -> EndpointMetrics | None:
        return self._metrics.get((installation_id, method.upper(), endpoint))

    def high_error_endpoints(self, installation_id: str, threshold_pct: float = 5.0) -> list[EndpointMetrics]:
        return [m for (inst, _, _), m in self._metrics.items() if inst == installation_id and m.error_rate >= threshold_pct]

    def slowest_endpoints(self, installation_id: str, limit: int = 5) -> list[EndpointMetrics]:
        metrics = [m for (inst, _, _), m in self._metrics.items() if inst == installation_id]
        return sorted(metrics, key=lambda m: -m.avg_latency)[:limit]

    def list_endpoints(self, installation_id: str) -> list[EndpointMetrics]:
        return [m for (inst, _, _), m in self._metrics.items() if inst == installation_id]
