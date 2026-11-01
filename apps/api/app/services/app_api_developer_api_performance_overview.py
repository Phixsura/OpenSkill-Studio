"""App API Developer API Performance Overview — unified performance metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PerformanceOverview:
    avg_latency_ms: float = 0.0
    p50_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    total_requests: int = 0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    slowest_endpoint: str = ""
    fastest_endpoint: str = ""

    @property
    def performance_grade(self) -> str:
        if self.p99_ms <= 200 and self.error_rate < 1: return "A"
        if self.p99_ms <= 500 and self.error_rate < 3: return "B"
        if self.p99_ms <= 1000 and self.error_rate < 5: return "C"
        return "D"

class AppAPIDeveloperAPIPerformanceOverview:
    def __init__(self) -> None:
        self._overviews: dict[str, PerformanceOverview] = {}

    def update(self, installation_id: str, **kwargs) -> PerformanceOverview:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._overviews:
            self._overviews[installation_id] = PerformanceOverview()
        o = self._overviews[installation_id]
        for k, v in kwargs.items():
            if hasattr(o, k): setattr(o, k, v)
        return o

    def get(self, installation_id: str) -> PerformanceOverview:
        return self._overviews.get(installation_id, PerformanceOverview())
