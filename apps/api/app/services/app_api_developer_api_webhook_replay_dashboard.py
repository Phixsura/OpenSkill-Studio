"""App API Developer Webhook Replay Dashboard — overview of replay operations."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ReplayDashboard:
    total_replayed: int = 0
    successful_replays: int = 0
    failed_replays: int = 0
    pending_replay: int = 0
    avg_replay_latency_ms: float = 0.0

    @property
    def replay_success_rate(self) -> float:
        total = self.successful_replays + self.failed_replays
        if total == 0: return 100.0
        return round(self.successful_replays / total * 100, 1)

class AppAPIDeveloperAPIWebhookReplayDashboard:
    def __init__(self) -> None:
        self._dashboards: dict[str, ReplayDashboard] = {}

    def update(self, installation_id: str, **kwargs) -> ReplayDashboard:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._dashboards:
            self._dashboards[installation_id] = ReplayDashboard()
        d = self._dashboards[installation_id]
        for k, v in kwargs.items():
            if hasattr(d, k): setattr(d, k, v)
        return d

    def get(self, installation_id: str) -> ReplayDashboard:
        return self._dashboards.get(installation_id, ReplayDashboard())
