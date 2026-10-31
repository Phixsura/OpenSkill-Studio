"""API Consumer Request Queue — queue and process requests asynchronously."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class QueueStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class QueuedRequest:
    request_id: str
    consumer_id: str
    method: str
    path: str
    status: QueueStatus = QueueStatus.QUEUED
    queued_at: float = field(default_factory=time.time)
    completed_at: float = 0.0
    result_status: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestQueue:
    def __init__(self, max_queue_size: int = 1000) -> None:
        self._queues: dict[str, list[QueuedRequest]] = {}
        self._max = max(10, max_queue_size)

    def enqueue(self, installation_id: str, request: QueuedRequest) -> QueuedRequest:
        if not installation_id: raise ValueError("installation_id is required")
        queue = self._queues.setdefault(installation_id, [])
        if len(queue) >= self._max: raise ValueError("Queue is full")
        queue.append(request)
        return request

    def dequeue(self, installation_id: str) -> QueuedRequest | None:
        queue = self._queues.get(installation_id, [])
        for r in queue:
            if r.status == QueueStatus.QUEUED:
                r.status = QueueStatus.PROCESSING
                return r
        return None

    def complete(self, installation_id: str, request_id: str, result_status: int) -> QueuedRequest:
        for r in self._queues.get(installation_id, []):
            if r.request_id == request_id:
                r.status = QueueStatus.COMPLETED if 200 <= result_status < 400 else QueueStatus.FAILED
                r.completed_at = time.time()
                r.result_status = result_status
                return r
        raise KeyError(f"Request {request_id} not found")

    def queue_depth(self, installation_id: str) -> int:
        return sum(1 for r in self._queues.get(installation_id, []) if r.status == QueueStatus.QUEUED)

    def stats(self, installation_id: str) -> dict[str, int]:
        queue = self._queues.get(installation_id, [])
        return {s.value: sum(1 for r in queue if r.status == s) for s in QueueStatus}
