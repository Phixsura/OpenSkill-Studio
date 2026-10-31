"""App API Developer Webhook Payload Size Analyzer — analyze payload sizes across destinations."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class PayloadSizeStats:
    destination: str
    total_payloads: int = 0
    total_bytes: int = 0
    min_bytes: int = 0
    max_bytes: int = 0
    oversized_count: int = 0

    @property
    def avg_bytes(self) -> float:
        return round(self.total_bytes / self.total_payloads, 1) if self.total_payloads > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiWebhookPayloadSizeAnalyzer:
    def __init__(self, max_payload_bytes: int = 1_048_576) -> None:
        self._max = max_payload_bytes
        self._stats: dict[tuple[str, str], PayloadSizeStats] = {}

    def record(self, installation_id: str, destination: str, payload_bytes: int) -> PayloadSizeStats:
        if not installation_id: raise ValueError("installation_id is required")
        if payload_bytes < 0: raise ValueError("payload_bytes must be non-negative")
        key = (installation_id, destination)
        if key not in self._stats:
            self._stats[key] = PayloadSizeStats(destination=destination, min_bytes=payload_bytes)
        s = self._stats[key]
        s.total_payloads += 1
        s.total_bytes += payload_bytes
        if payload_bytes < s.min_bytes: s.min_bytes = payload_bytes
        if payload_bytes > s.max_bytes: s.max_bytes = payload_bytes
        if payload_bytes > self._max: s.oversized_count += 1
        return s

    def get(self, installation_id: str, destination: str) -> PayloadSizeStats | None:
        return self._stats.get((installation_id, destination))

    def oversized_destinations(self, installation_id: str) -> list[PayloadSizeStats]:
        return [s for (inst, _), s in self._stats.items() if inst == installation_id and s.oversized_count > 0]

    def largest_avg(self, installation_id: str, limit: int = 5) -> list[PayloadSizeStats]:
        stats = [s for (inst, _), s in self._stats.items() if inst == installation_id]
        return sorted(stats, key=lambda s: s.avg_bytes, reverse=True)[:limit]

    def total_bandwidth(self, installation_id: str) -> int:
        return sum(s.total_bytes for (inst, _), s in self._stats.items() if inst == installation_id)
