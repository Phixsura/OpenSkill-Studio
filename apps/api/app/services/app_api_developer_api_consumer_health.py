"""App API Developer Consumer Health — track health of API consumers."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerHealth:
    consumer_id: str
    status: str = "healthy"  # "healthy", "degraded", "inactive"
    error_rate: float = 0.0
    last_seen: str = ""
    total_requests: int = 0

class AppAPIDeveloperAPIConsumerHealth:
    def __init__(self) -> None:
        self._health: dict[tuple[str, str], ConsumerHealth] = {}

    def update(self, installation_id: str, consumer_id: str, error_rate: float, total_requests: int, last_seen: str = "") -> ConsumerHealth:
        if not installation_id: raise ValueError("installation_id is required")
        status = "healthy"
        if error_rate > 10: status = "degraded"
        elif total_requests == 0: status = "inactive"
        h = ConsumerHealth(consumer_id=consumer_id, status=status, error_rate=error_rate, last_seen=last_seen, total_requests=total_requests)
        self._health[(installation_id, consumer_id)] = h
        return h

    def unhealthy(self, installation_id: str) -> list[ConsumerHealth]:
        return [h for (inst, _), h in self._health.items() if inst == installation_id and h.status != "healthy"]

    def list_all(self, installation_id: str) -> list[ConsumerHealth]:
        return [h for (inst, _), h in self._health.items() if inst == installation_id]
