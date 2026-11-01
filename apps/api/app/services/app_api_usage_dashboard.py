"""App API Usage Dashboard — consolidated usage metrics dashboard."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class UsageDashboard:
    total_requests: int = 0
    total_errors: int = 0
    unique_consumers: int = 0
    unique_endpoints: int = 0
    avg_latency_ms: float = 0.0
    peak_rpm: int = 0
    quota_usage_pct: float = 0.0

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.total_errors / self.total_requests * 100, 2)

class AppAPIUsageDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, UsageDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> UsageDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = UsageDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> UsageDashboard:
        return self._dashboards.get(installation_id, UsageDashboard())
