"""App API Developer API Usage Dashboard — THE comprehensive API usage dashboard."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class APIUsageDashboard:
    total_requests_24h: int = 0
    total_requests_7d: int = 0
    total_requests_30d: int = 0
    unique_consumers_24h: int = 0
    unique_endpoints: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    error_rate_pct: float = 0.0
    top_endpoint: str = ""
    top_consumer: str = ""
    webhook_deliveries_24h: int = 0
    cache_hit_rate_pct: float = 0.0

    @property
    def daily_growth_pct(self) -> float:
        if self.total_requests_7d == 0: return 0.0
        avg_daily = self.total_requests_7d / 7
        return round((self.total_requests_24h - avg_daily) / avg_daily * 100, 1) if avg_daily > 0 else 0.0

    @property
    def health(self) -> str:
        if self.error_rate_pct < 0.5 and self.p99_latency_ms < 300: return "excellent"
        if self.error_rate_pct < 2 and self.p99_latency_ms < 1000: return "good"
        if self.error_rate_pct < 5: return "fair"
        return "poor"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiUsageDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, APIUsageDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> APIUsageDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        d = APIUsageDashboard()
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        self._dashboards[installation_id] = d
        return d

    def get(self, installation_id: str) -> APIUsageDashboard:
        return self._dashboards.get(installation_id, APIUsageDashboard())
