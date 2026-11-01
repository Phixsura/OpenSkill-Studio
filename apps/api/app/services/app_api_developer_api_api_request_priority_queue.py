"""App API Developer API Request Priority Queue — prioritized request processing."""
from __future__ import annotations
from dataclasses import dataclass, field
import heapq
import time
import structlog

log = structlog.get_logger()

PRIORITY_MAP = {"critical": 0, "high": 1, "normal": 2, "low": 3}

@dataclass
class PrioritizedRequest:
    request_id: str
    priority: str
    endpoint: str
    enqueued_at: float = field(default_factory=time.time)
    processed: bool = False

    def __lt__(self, other: PrioritizedRequest) -> bool:
        return PRIORITY_MAP.get(self.priority, 2) < PRIORITY_MAP.get(other.priority, 2)

class AppAPIDeveloperAPIApiRequestPriorityQueue:
    def __init__(self) -> None:
        self._queues: dict[str, list[PrioritizedRequest]] = {}
        self._stats: dict[str, dict[str, int]] = {}

    def enqueue(self, installation_id: str, request_id: str, priority: str, endpoint: str) -> PrioritizedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        if priority not in PRIORITY_MAP: raise ValueError(f"Invalid priority: {priority}")
        r = PrioritizedRequest(request_id=request_id, priority=priority, endpoint=endpoint)
        q = self._queues.setdefault(installation_id, [])
        heapq.heappush(q, r)
        s = self._stats.setdefault(installation_id, {p: 0 for p in PRIORITY_MAP})
        s[priority] = s.get(priority, 0) + 1
        return r

    def dequeue(self, installation_id: str) -> PrioritizedRequest | None:
        q = self._queues.get(installation_id, [])
        if not q: return None
        r = heapq.heappop(q)
        r.processed = True
        return r

    def peek(self, installation_id: str) -> PrioritizedRequest | None:
        q = self._queues.get(installation_id, [])
        return q[0] if q else None

    def queue_size(self, installation_id: str) -> int:
        return len(self._queues.get(installation_id, []))

    def priority_distribution(self, installation_id: str) -> dict[str, int]:
        return dict(self._stats.get(installation_id, {}))
