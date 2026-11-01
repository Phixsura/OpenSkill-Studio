"""Endpoint Health Score — compute a composite health score per endpoint."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class EndpointMetrics:
    endpoint_path: str
    uptime_pct: float        # 0-100
    avg_latency_ms: float
    error_rate_pct: float    # 0-100
    p99_latency_ms: float
    request_count: int

@dataclass
class HealthScore:
    endpoint_path: str
    score: float             # 0-100
    grade: str               # A, B, C, D, F
    uptime_score: float
    latency_score: float
    error_score: float
    status: str              # "healthy", "degraded", "unhealthy"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointHealthScore:
    def __init__(self) -> None:
        self._metrics: dict[tuple[str, str], EndpointMetrics] = {}

    def record_metrics(self, installation_id: str, metrics: EndpointMetrics) -> EndpointMetrics:
        if not installation_id:
            raise ValueError("installation_id is required")
        self._metrics[(installation_id, metrics.endpoint_path)] = metrics
        return metrics

    def compute(self, installation_id: str, endpoint_path: str) -> HealthScore:
        m = self._metrics.get((installation_id, endpoint_path))
        if not m:
            raise ValueError("No metrics recorded")
        # Uptime score: 100 at 100%, drops fast below 99%
        uptime_s = min(100, max(0, (m.uptime_pct - 95) * 20))
        # Latency score: 100 at 0ms, 0 at 2000ms+
        latency_s = min(100, max(0, 100 - (m.avg_latency_ms / 20)))
        # Error score: 100 at 0%, 0 at 10%+
        error_s = min(100, max(0, 100 - m.error_rate_pct * 10))
        # Weighted composite
        score = round(uptime_s * 0.4 + latency_s * 0.3 + error_s * 0.3, 1)
        # Grade
        if score >= 90: grade = "A"
        elif score >= 75: grade = "B"
        elif score >= 60: grade = "C"
        elif score >= 40: grade = "D"
        else: grade = "F"
        # Status
        if score >= 80: status = "healthy"
        elif score >= 50: status = "degraded"
        else: status = "unhealthy"
        return HealthScore(endpoint_path=endpoint_path, score=score, grade=grade, uptime_score=round(uptime_s, 1), latency_score=round(latency_s, 1), error_score=round(error_s, 1), status=status)

    def compute_all(self, installation_id: str) -> list[HealthScore]:
        paths = [p for (inst, p) in self._metrics if inst == installation_id]
        return sorted([self.compute(installation_id, p) for p in paths], key=lambda h: h.score, reverse=True)
