"""App API Developer API Gateway Analytics — track gateway-level performance metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class GatewayAnalytics:
    total_requests: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    cache_hit_rate_pct: float = 0.0
    rate_limited_requests: int = 0
    auth_failures: int = 0
    upstream_errors: int = 0

    @property
    def error_rate_pct(self) -> float:
        return round(self.total_errors / self.total_requests * 100, 2) if self.total_requests > 0 else 0.0

    @property
    def health(self) -> str:
        if self.error_rate_pct < 0.1 and self.p99_latency_ms < 200: return "excellent"
        if self.error_rate_pct < 1 and self.p99_latency_ms < 500: return "good"
        if self.error_rate_pct < 5: return "fair"
        return "poor"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformApiGatewayAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, GatewayAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> GatewayAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        a = GatewayAnalytics()
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        self._analytics[installation_id] = a
        return a

    def get(self, installation_id: str) -> GatewayAnalytics:
        return self._analytics.get(installation_id, GatewayAnalytics())
