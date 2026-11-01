"""App API Developer Webhook Destination Stats — per-destination delivery stats."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DestinationStats:
    destination: str
    total_delivered: int = 0
    total_failed: int = 0
    avg_latency_ms: float = 0.0
    last_status_code: int = 0

    @property
    def success_rate(self) -> float:
        total = self.total_delivered + self.total_failed
        if total == 0: return 100.0
        return round(self.total_delivered / total * 100, 1)

class AppAPIDeveloperAPIWebhookDestinationStats:
    def __init__(self) -> None:
        self._stats: dict[tuple[str, str], DestinationStats] = {}

    def record(self, installation_id: str, destination: str, success: bool, latency_ms: float, status_code: int) -> DestinationStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._stats:
            self._stats[key] = DestinationStats(destination=destination)
        s = self._stats[key]
        if success: s.total_delivered += 1
        else: s.total_failed += 1
        total = s.total_delivered + s.total_failed
        s.avg_latency_ms = round(((s.avg_latency_ms * (total - 1)) + latency_ms) / total, 1)
        s.last_status_code = status_code
        return s

    def top_destinations(self, installation_id: str, limit: int = 10) -> list[DestinationStats]:
        stats = [s for (inst, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: s.total_delivered + s.total_failed, reverse=True)[:limit]

    def failing_destinations(self, installation_id: str, threshold: float = 90.0) -> list[DestinationStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id and s.success_rate < threshold]

    def list_stats(self, installation_id: str) -> list[DestinationStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id]
