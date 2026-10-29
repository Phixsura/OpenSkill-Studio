"""App API Developer API Error Analytics — comprehensive error analysis."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorAnalytics:
    total_errors: int = 0
    unique_error_codes: int = 0
    top_error_code: str = ""
    top_error_count: int = 0
    error_rate_trend: str = "stable"  # "increasing", "decreasing", "stable"
    errors_by_status: dict[str, int] = field(default_factory=dict)
    most_affected_endpoint: str = ""

class AppAPIDeveloperAPIErrorAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, ErrorAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> ErrorAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._analytics:
            self._analytics[installation_id] = ErrorAnalytics()
        a = self._analytics[installation_id]
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        return a

    def get(self, installation_id: str) -> ErrorAnalytics:
        return self._analytics.get(installation_id, ErrorAnalytics())
