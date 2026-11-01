"""API Consumer Request Queue Priority — prioritize request queues per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import structlog

log = structlog.get_logger()

@dataclass
class PrioritizedRequest:
    request_id: str
    consumer_id: str
    endpoint: str
    priority: int  # 1=highest, 10=lowest
    enqueued_order: int = 0

    def __lt__(self, other: "PrioritizedRequest") -> bool:
        return (self.priority, self.enqueued_order) < (other.priority, other.enqueued_order)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRequestQueuePriority:
    def __init__(self, max_queue: int = 5000) -> None:
        self._queues: dict[str, list[PrioritizedRequest]] = {}
        self._max = max(100, max_queue)
        self._counter: dict[str, int] = {}

    def enqueue(self, installation_id: str, request: PrioritizedRequest) -> PrioritizedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        if not 1 <= request.priority <= 10: raise ValueError("priority must be 1-10")
        queue = self._queues.setdefault(installation_id, [])
        if len(queue) >= self._max: raise ValueError("Queue full")
        self._counter[installation_id] = self._counter.get(installation_id, 0) + 1
        request.enqueued_order = self._counter[installation_id]
        heapq.heappush(queue, request)
        return request

    def dequeue(self, installation_id: str) -> PrioritizedRequest | None:
        queue = self._queues.get(installation_id, [])
        return heapq.heappop(queue) if queue else None

    def depth(self, installation_id: str) -> int:
        return len(self._queues.get(installation_id, []))

    def peek(self, installation_id: str) -> PrioritizedRequest | None:
        queue = self._queues.get(installation_id, [])
        return queue[0] if queue else None
