"""App API Developer Rate Limit Dashboard — unified rate limiting overview."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitDashboard:
    total_rules: int = 0
    active_rules: int = 0
    throttled_requests: int = 0
    total_consumers: int = 0
    exhausted_consumers: int = 0
    avg_utilization_pct: float = 0.0

class AppAPIDeveloperAPIRateLimitDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, RateLimitDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> RateLimitDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = RateLimitDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> RateLimitDashboard:
        return self._dashboards.get(installation_id, RateLimitDashboard())
