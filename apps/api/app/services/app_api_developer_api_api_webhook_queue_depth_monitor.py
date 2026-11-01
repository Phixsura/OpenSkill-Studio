"""App API Developer Webhook Queue Depth Monitor — track delivery queue backlog."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class QueueSnapshot:
    destination: str
    depth: int
    oldest_age_seconds: float
    processing_rate_per_sec: float
    timestamp: float = field(default_factory=time.time)

    @property
    def estimated_drain_seconds(self) -> float:
        if self.processing_rate_per_sec <= 0: return float("inf")
        return round(self.depth / self.processing_rate_per_sec, 1)

    @property
    def backlogged(self) -> bool:
        return self.depth > 1000 or self.oldest_age_seconds > 300

class AppAPIDeveloperAPIApiWebhookQueueDepthMonitor:
    def __init__(self) -> None:
        self._snapshots: dict[tuple[str, str], list[QueueSnapshot]] = {}

    def record(self, installation_id: str, destination: str, depth: int, oldest_age_seconds: float, processing_rate: float) -> QueueSnapshot:
        if not installation_id: raise ValueError("installation_id is required")
        if depth < 0: raise ValueError("depth must be non-negative")
        s = QueueSnapshot(destination=destination, depth=depth, oldest_age_seconds=oldest_age_seconds, processing_rate_per_sec=processing_rate)
        self._snapshots.setdefault((installation_id, destination), []).append(s)
        return s

    def latest(self, installation_id: str) -> list[QueueSnapshot]:
        result = []
        for (inst, dest), snaps in self._snapshots.items():
            if inst == installation_id and snaps:
                result.append(snaps[-1])
        return result

    def backlogged(self, installation_id: str) -> list[QueueSnapshot]:
        return [s for s in self.latest(installation_id) if s.backlogged]

    def total_depth(self, installation_id: str) -> int:
        return sum(s.depth for s in self.latest(installation_id))
