"""Consumer API Request Priority Queue — prioritize requests by consumer tier and endpoint."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
import heapq
import structlog

log = structlog.get_logger()

@dataclass
class PriorityRequest:
    request_id: str
    consumer_id: str
    endpoint: str
    priority: int = 0  # higher = more important
    weight: float = 1.0
    enqueued_at: datetime | None = None
    status: str = "queued"

    def __lt__(self, other: PriorityRequest) -> bool:
        if self.priority != other.priority:
            return self.priority > other.priority
        return (self.enqueued_at or datetime.min) < (other.enqueued_at or datetime.min)

@dataclass
class QueuePosition:
    request_id: str
    position: int
    estimated_wait_ms: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiRequestPriorityQueue:
    def __init__(self, max_size: int = 10000) -> None:
        self._queues: dict[str, list[PriorityRequest]] = {}  # inst -> heap
        self._max = max_size
        self._processed: dict[str, int] = {}

    def enqueue(self, installation_id: str, request: PriorityRequest) -> PriorityRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if installation_id not in self._queues:
            self._queues[installation_id] = []
        if len(self._queues[installation_id]) >= self._max:
            raise ValueError("Queue full")
        request.enqueued_at = request.enqueued_at or datetime.utcnow()
        request.status = "queued"
        heapq.heappush(self._queues[installation_id], request)
        return request

    def dequeue(self, installation_id: str) -> PriorityRequest | None:
        queue = self._queues.get(installation_id, [])
        if not queue:
            return None
        request = heapq.heappop(queue)
        request.status = "processing"
        self._processed[installation_id] = self._processed.get(installation_id, 0) + 1
        return request

    def peek(self, installation_id: str) -> PriorityRequest | None:
        queue = self._queues.get(installation_id, [])
        return queue[0] if queue else None

    def get_position(self, installation_id: str, request_id: str) -> QueuePosition | None:
        queue = self._queues.get(installation_id, [])
        sorted_q = sorted(queue)
        for i, r in enumerate(sorted_q):
            if r.request_id == request_id:
                return QueuePosition(request_id=request_id, position=i + 1, estimated_wait_ms=(i + 1) * 100)
        return None

    def size(self, installation_id: str) -> int:
        return len(self._queues.get(installation_id, []))

    def processed_count(self, installation_id: str) -> int:
        return self._processed.get(installation_id, 0)
