"""App API Webhook Payload Size — track and limit payload sizes."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class PayloadSizeStats:
    destination: str
    total_bytes: int = 0
    max_bytes: int = 0
    delivery_count: int = 0
    over_limit_count: int = 0

    @property
    def avg_bytes(self) -> float:
        if self.delivery_count == 0: return 0.0
        return round(self.total_bytes / self.delivery_count, 1)

class AppAPIWebhookPayloadSize:
    def __init__(self, max_payload_bytes: int = 1048576) -> None:
        self._max = max_payload_bytes
        self._stats: dict[tuple[str, str], PayloadSizeStats] = {}

    def record(self, installation_id: str, destination: str, size_bytes: int) -> PayloadSizeStats:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, destination)
        if key not in self._stats:
            self._stats[key] = PayloadSizeStats(destination=destination)
        s = self._stats[key]
        s.total_bytes += size_bytes
        s.delivery_count += 1
        if size_bytes > s.max_bytes: s.max_bytes = size_bytes
        if size_bytes > self._max: s.over_limit_count += 1
        return s

    def is_over_limit(self, size_bytes: int) -> bool:
        return size_bytes > self._max

    def list_stats(self, installation_id: str) -> list[PayloadSizeStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id]
