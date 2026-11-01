"""App API Developer Webhook Delivery Priority — prioritize webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

PRIORITY_ORDER = {"critical": 0, "high": 1, "normal": 2, "low": 3, "bulk": 4}

@dataclass
class PriorityQueue:
    destination: str
    queued: dict[str, int] = field(default_factory=lambda: {p: 0 for p in PRIORITY_ORDER})
    delivered: dict[str, int] = field(default_factory=lambda: {p: 0 for p in PRIORITY_ORDER})

    @property
    def total_queued(self) -> int:
        return sum(self.queued.values())

    @property
    def total_delivered(self) -> int:
        return sum(self.delivered.values())

class AppAPIDeveloperPlatformSDKApiWebhookDeliveryPriority:
    def __init__(self) -> None:
        self._queues: dict[tuple[str, str], PriorityQueue] = {}

    def enqueue(self, installation_id: str, destination: str, priority: str, count: int = 1) -> PriorityQueue:
        if not installation_id: raise ValueError("installation_id is required")
        if priority not in PRIORITY_ORDER: raise ValueError(f"Invalid priority: {priority}")
        key = (installation_id, destination)
        if key not in self._queues:
            self._queues[key] = PriorityQueue(destination=destination)
        q = self._queues[key]
        q.queued[priority] += count
        return q

    def deliver(self, installation_id: str, destination: str, priority: str, count: int = 1) -> PriorityQueue:
        key = (installation_id, destination)
        q = self._queues.get(key)
        if q is None: raise KeyError(f"No queue for {destination}")
        q.queued[priority] = max(0, q.queued[priority] - count)
        q.delivered[priority] += count
        return q

    def next_priority(self, installation_id: str, destination: str) -> str | None:
        key = (installation_id, destination)
        q = self._queues.get(key)
        if q is None: return None
        for p in sorted(PRIORITY_ORDER, key=PRIORITY_ORDER.get):
            if q.queued.get(p, 0) > 0: return p
        return None

    def all_queues(self, installation_id: str) -> list[PriorityQueue]:
        return [q for (inst, _), q in self._queues.items() if inst == installation_id]
