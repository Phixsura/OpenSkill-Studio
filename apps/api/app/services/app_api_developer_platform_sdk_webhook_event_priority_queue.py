"""App API Developer Webhook Event Priority Queue — prioritize event processing."""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import structlog

log = structlog.get_logger()

PRIORITY_MAP = {"critical": 0, "high": 1, "normal": 2, "low": 3}

@dataclass
class PrioritizedEvent:
    event_id: str
    event_type: str
    priority: str
    destination: str
    processed: bool = False

    def __lt__(self, other: PrioritizedEvent) -> bool:
        return PRIORITY_MAP.get(self.priority, 99) < PRIORITY_MAP.get(other.priority, 99)

class AppAPIDeveloperPlatformSDKWebhookEventPriorityQueue:
    def __init__(self) -> None:
        self._queues: dict[str, list[PrioritizedEvent]] = {}
        self._processed: dict[str, int] = {}

    def enqueue(self, installation_id: str, event_id: str, event_type: str, priority: str, destination: str) -> PrioritizedEvent:
        if not installation_id: raise ValueError("installation_id is required")
        if priority not in PRIORITY_MAP: raise ValueError(f"Invalid priority: {priority}")
        e = PrioritizedEvent(event_id=event_id, event_type=event_type, priority=priority, destination=destination)
        q = self._queues.setdefault(installation_id, [])
        heapq.heappush(q, e)
        return e

    def dequeue(self, installation_id: str) -> PrioritizedEvent | None:
        q = self._queues.get(installation_id, [])
        if not q: return None
        e = heapq.heappop(q)
        e.processed = True
        self._processed[installation_id] = self._processed.get(installation_id, 0) + 1
        return e

    def queue_size(self, installation_id: str) -> int:
        return len(self._queues.get(installation_id, []))

    def processed_count(self, installation_id: str) -> int:
        return self._processed.get(installation_id, 0)
