"""App API Developer Webhook Destination Health — monitor health per destination."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DestinationHealth:
    destination: str
    total_deliveries: int = 0
    successful: int = 0
    failed: int = 0
    avg_response_ms: float = 0.0
    last_failure_at: float = 0.0
    consecutive_failures: int = 0

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def status(self) -> str:
        if self.consecutive_failures >= 10: return "down"
        if self.consecutive_failures >= 3: return "degraded"
        if self.success_rate < 90: return "unhealthy"
        return "healthy"

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookDestinationHealth:
    def __init__(self) -> None:
        self._health: dict[tuple[str, str], DestinationHealth] = {}

    def record(self, installation_id: str, destination: str, success: bool, response_ms: float) -> DestinationHealth:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._health:
            self._health[key] = DestinationHealth(destination=destination)
        h = self._health[key]
        h.total_deliveries += 1
        if success:
            h.successful += 1
            h.consecutive_failures = 0
        else:
            h.failed += 1
            h.consecutive_failures += 1
            h.last_failure_at = time.time()
        # Running average
        h.avg_response_ms = round(((h.avg_response_ms * (h.total_deliveries - 1)) + response_ms) / h.total_deliveries, 1)
        return h

    def get(self, installation_id: str, destination: str) -> DestinationHealth | None:
        return self._health.get((installation_id, destination))

    def unhealthy(self, installation_id: str) -> list[DestinationHealth]:
        return [h for (inst, _), h in self._health.items() if inst == installation_id and h.status != "healthy"]

    def all_destinations(self, installation_id: str) -> list[DestinationHealth]:
        return [h for (inst, _), h in self._health.items() if inst == installation_id]
