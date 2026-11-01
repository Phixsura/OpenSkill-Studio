"""Consumer API Endpoint Metric Aggregator — aggregate metrics across endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class EndpointMetric:
    endpoint_path: str
    request_count: int = 0
    error_count: int = 0
    total_latency_ms: float = 0.0
    min_latency_ms: float = float("inf")
    max_latency_ms: float = 0.0

    @property
    def avg_latency_ms(self) -> float:
        return self.total_latency_ms / max(self.request_count, 1)

    @property
    def error_rate_pct(self) -> float:
        return (self.error_count / max(self.request_count, 1)) * 100

@dataclass
class AggregatedMetrics:
    total_requests: int
    total_errors: int
    overall_error_rate: float
    overall_avg_latency: float
    top_endpoints: list[EndpointMetric]
    slowest_endpoints: list[EndpointMetric]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiEndpointMetricAggregator:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], EndpointMetric] = {}

    def record(self, installation_id: str, endpoint_path: str, latency_ms: float, is_error: bool = False) -> EndpointMetric:
        if not installation_id:
            raise ValueError("installation_id is required")
        if latency_ms < 0:
            raise ValueError("latency must be non-negative")
        key = (installation_id, endpoint_path)
        if key not in self._metrics:
            self._metrics[key] = EndpointMetric(endpoint_path=endpoint_path)
        m = self._metrics[key]
        m.request_count += 1
        m.total_latency_ms += latency_ms
        m.min_latency_ms = min(m.min_latency_ms, latency_ms)
        m.max_latency_ms = max(m.max_latency_ms, latency_ms)
        if is_error:
            m.error_count += 1
        return m

    def aggregate(self, installation_id: str, top_n: int = 5) -> AggregatedMetrics:
        metrics = [m for (inst, _), m in self._metrics.items() if inst == installation_id]
        if not metrics:
            return AggregatedMetrics(total_requests=0, total_errors=0, overall_error_rate=0, overall_avg_latency=0, top_endpoints=[], slowest_endpoints=[])
        total_req = sum(m.request_count for m in metrics)
        total_err = sum(m.error_count for m in metrics)
        total_lat = sum(m.total_latency_ms for m in metrics)
        return AggregatedMetrics(
            total_requests=total_req, total_errors=total_err,
            overall_error_rate=round(total_err / max(total_req, 1) * 100, 2),
            overall_avg_latency=round(total_lat / max(total_req, 1), 1),
            top_endpoints=sorted(metrics, key=lambda m: -m.request_count)[:top_n],
            slowest_endpoints=sorted(metrics, key=lambda m: -m.avg_latency_ms)[:top_n],
        )

    def get_metric(self, installation_id: str, endpoint_path: str) -> EndpointMetric | None:
        return self._metrics.get((installation_id, endpoint_path))
