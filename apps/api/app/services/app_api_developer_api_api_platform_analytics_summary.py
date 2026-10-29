"""App API Developer Platform Analytics Summary — comprehensive analytics overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class AnalyticsSummary:
    # Traffic
    total_requests_7d: int = 0
    total_requests_30d: int = 0
    unique_consumers_7d: int = 0
    # Performance
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    # Growth
    request_growth_pct: float = 0.0
    consumer_growth_pct: float = 0.0
    # Top
    top_endpoint: str = ""
    top_consumer: str = ""
    top_error_code: str = ""
    # Webhooks
    webhook_delivery_rate_pct: float = 100.0
    webhook_avg_latency_ms: float = 0.0

    @property
    def health_indicator(self) -> str:
        if self.error_rate_pct > 5 or self.p99_latency_ms > 2000: return "poor"
        if self.error_rate_pct > 1 or self.p99_latency_ms > 1000: return "fair"
        if self.error_rate_pct > 0.1: return "good"
        return "excellent"

class AppAPIDeveloperAPIApiPlatformAnalyticsSummary:
    def __init__(self) -> None:
        self._summaries: dict[str, AnalyticsSummary] = {}

    def update(self, installation_id: str, **kwargs) -> AnalyticsSummary:
        if not installation_id: raise ValueError("installation_id is required")
        s = AnalyticsSummary()
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        self._summaries[installation_id] = s
        return s

    def get(self, installation_id: str) -> AnalyticsSummary:
        return self._summaries.get(installation_id, AnalyticsSummary())
