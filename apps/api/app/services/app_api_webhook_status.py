"""App API Webhook Status — track webhook destination health status."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class DestinationStatus:
    destination: str
    status: str = "unknown"  # "healthy", "degraded", "down", "unknown"
    consecutive_successes: int = 0
    consecutive_failures: int = 0

class AppAPIWebhookStatus:
    def __init__(self) -> None:
        self._statuses: dict[tuple[str, str], DestinationStatus] = {}

    def record(self, installation_id: str, destination: str, success: bool) -> DestinationStatus:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._statuses:
            self._statuses[key] = DestinationStatus(destination=destination)
        s = self._statuses[key]
        if success:
            s.consecutive_successes += 1
            s.consecutive_failures = 0
            s.status = "healthy"
        else:
            s.consecutive_failures += 1
            s.consecutive_successes = 0
            s.status = "down" if s.consecutive_failures >= 3 else "degraded"
        return s

    def get_status(self, installation_id: str, destination: str) -> DestinationStatus:
        return self._statuses.get((installation_id, destination), DestinationStatus(destination=destination))

    def unhealthy(self, installation_id: str) -> list[DestinationStatus]:
        return [s for (inst, _), s in self._statuses.items() if inst == installation_id and s.status in ("degraded", "down")]

    def list_all(self, installation_id: str) -> list[DestinationStatus]:
        return [s for (inst, _), s in self._statuses.items() if inst == installation_id]
