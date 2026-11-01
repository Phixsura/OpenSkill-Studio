"""App API Developer Quick Stats — at-a-glance platform numbers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class QuickStats:
    requests_today: int = 0
    errors_today: int = 0
    active_developers: int = 0
    webhook_deliveries_today: int = 0
    avg_response_ms: float = 0.0
    uptime_today: float = 100.0

class AppAPIDeveloperAPIQuickStats:
    def __init__(self) -> None:
        self._stats: dict[str, QuickStats] = {}

    def update(self, installation_id: str, **kwargs) -> QuickStats:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._stats:
            self._stats[installation_id] = QuickStats()
        s = self._stats[installation_id]
        for k, v in kwargs.items():
            if hasattr(s, k): setattr(s, k, v)
        return s

    def get(self, installation_id: str) -> QuickStats:
        return self._stats.get(installation_id, QuickStats())
