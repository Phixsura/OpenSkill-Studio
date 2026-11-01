"""API Consumer Webhook Priority Queue — prioritize webhook delivery by event importance."""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import time
import structlog

log = structlog.get_logger()

@dataclass
class PrioritizedEvent:
    event_id: str
    event_type: str
    consumer_id: str
    priority: int  # 1=highest, 10=lowest
    payload_size: int = 0
    enqueued_at: float = field(default_factory=time.time)

    def __lt__(self, other: PrioritizedEvent) -> bool:
        return (self.priority, self.enqueued_at) < (other.priority, other.enqueued_at)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookPriorityQueue:
    def __init__(self, max_queue_size: int = 10000) -> None:
        self._queues: dict[str, list[PrioritizedEvent]] = {}
        self._max = max(100, max_queue_size)
        self._stats: dict[str, dict[str, int]] = {}

    def enqueue(self, installation_id: str, event: PrioritizedEvent) -> PrioritizedEvent:
        if not installation_id: raise ValueError("installation_id is required")
        if not 1 <= event.priority <= 10: raise ValueError("priority must be 1-10")
        queue = self._queues.setdefault(installation_id, [])
        if len(queue) >= self._max: raise ValueError("Queue is full")
        heapq.heappush(queue, event)
        stats = self._stats.setdefault(installation_id, {"enqueued": 0, "dequeued": 0})
        stats["enqueued"] += 1
        return event

    def dequeue(self, installation_id: str) -> PrioritizedEvent | None:
        queue = self._queues.get(installation_id, [])
        if not queue: return None
        event = heapq.heappop(queue)
        self._stats.setdefault(installation_id, {"enqueued": 0, "dequeued": 0})["dequeued"] += 1
        return event

    def peek(self, installation_id: str) -> PrioritizedEvent | None:
        queue = self._queues.get(installation_id, [])
        return queue[0] if queue else None

    def depth(self, installation_id: str) -> int:
        return len(self._queues.get(installation_id, []))

    def stats(self, installation_id: str) -> dict[str, int]:
        return self._stats.get(installation_id, {"enqueued": 0, "dequeued": 0})
