"""Consumer API Request Throttle Queue — queue and throttle excess requests."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import heapq
import structlog

log = structlog.get_logger()

@dataclass
class QueuedRequest:
    request_id: str
    consumer_id: str
    priority: int = 0  # higher = more important
    method: str = "GET"
    path: str = "/"
    queued_at: datetime | None = None
    status: str = "queued"  # "queued", "processing", "completed", "dropped"

    def __lt__(self, other: QueuedRequest) -> bool:
        return self.priority > other.priority  # higher priority first

@dataclass
class ThrottleConfig:
    consumer_id: str
    max_queue_size: int = 100
    max_concurrent: int = 10
    queue_timeout_seconds: int = 30

@dataclass
class QueueStats:
    queued: int
    processing: int
    completed: int
    dropped: int
    max_queue_size: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestThrottleQueue:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], ThrottleConfig] = {}
        self._queues: dict[tuple[str, str], list[QueuedRequest]] = {}
        self._stats: dict[tuple[str, str], dict[str, int]] = {}

    def configure(self, installation_id: str, config: ThrottleConfig) -> ThrottleConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.max_concurrent < 1:
            raise ValueError("max_concurrent must be positive")
        self._configs[(installation_id, config.consumer_id)] = config
        return config

    def enqueue(self, installation_id: str, request: QueuedRequest) -> QueuedRequest:
        key = (installation_id, request.consumer_id)
        config = self._configs.get(key, ThrottleConfig(consumer_id=request.consumer_id))
        if key not in self._queues:
            self._queues[key] = []
        if key not in self._stats:
            self._stats[key] = {"queued": 0, "processing": 0, "completed": 0, "dropped": 0}
        if len(self._queues[key]) >= config.max_queue_size:
            request.status = "dropped"
            self._stats[key]["dropped"] += 1
            return request
        request.status = "queued"
        request.queued_at = request.queued_at or datetime.utcnow()
        heapq.heappush(self._queues[key], request)
        self._stats[key]["queued"] += 1
        return request

    def dequeue(self, installation_id: str, consumer_id: str) -> QueuedRequest | None:
        key = (installation_id, consumer_id)
        queue = self._queues.get(key, [])
        if not queue:
            return None
        request = heapq.heappop(queue)
        request.status = "processing"
        stats = self._stats.get(key, {"queued": 0, "processing": 0, "completed": 0, "dropped": 0})
        stats["queued"] = max(0, stats["queued"] - 1)
        stats["processing"] += 1
        return request

    def complete(self, installation_id: str, consumer_id: str, request_id: str) -> None:
        key = (installation_id, consumer_id)
        stats = self._stats.get(key, {"queued": 0, "processing": 0, "completed": 0, "dropped": 0})
        stats["processing"] = max(0, stats["processing"] - 1)
        stats["completed"] += 1

    def get_stats(self, installation_id: str, consumer_id: str) -> QueueStats:
        key = (installation_id, consumer_id)
        config = self._configs.get(key, ThrottleConfig(consumer_id=consumer_id))
        s = self._stats.get(key, {"queued": 0, "processing": 0, "completed": 0, "dropped": 0})
        return QueueStats(queued=s["queued"], processing=s["processing"], completed=s["completed"], dropped=s["dropped"], max_queue_size=config.max_queue_size)
