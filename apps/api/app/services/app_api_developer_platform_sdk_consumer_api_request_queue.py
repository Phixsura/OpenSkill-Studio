"""Request Queue Manager — priority queue with concurrency limits."""
from __future__ import annotations

import heapq
import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class QueuedRequest:
    request_id: str
    consumer_id: str
    endpoint_id: str
    priority: int = 0  # lower = higher priority
    enqueued_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "queued"  # queued, processing, completed, failed


@dataclass
class RequestQueueManager:
    """Priority-based request queue with concurrency control."""

    _queue: list[tuple[int, int, QueuedRequest]] = field(default_factory=list)
    _processing: dict[str, QueuedRequest] = field(default_factory=dict)
    _completed: list[QueuedRequest] = field(default_factory=list)
    _max_concurrent: int = 10
    _counter: int = 0

    def configure(self, max_concurrent: int) -> dict:
        if max_concurrent < 1:
            raise ValueError("max_concurrent must be at least 1")
        self._max_concurrent = max_concurrent
        return {"max_concurrent": max_concurrent}

    def enqueue(self, request: QueuedRequest) -> dict:
        self._counter += 1
        heapq.heappush(self._queue, (request.priority, self._counter, request))
        logger.info("request_enqueued", request_id=request.request_id,
                     priority=request.priority)
        return {"request_id": request.request_id, "position": len(self._queue),
                "queue_size": len(self._queue)}

    def dequeue(self) -> dict | None:
        if len(self._processing) >= self._max_concurrent:
            return {"error": "at_capacity", "processing": len(self._processing),
                    "max": self._max_concurrent}
        if not self._queue:
            return None
        _, _, request = heapq.heappop(self._queue)
        request.status = "processing"
        self._processing[request.request_id] = request
        logger.info("request_dequeued", request_id=request.request_id)
        return {"request_id": request.request_id, "consumer_id": request.consumer_id,
                "endpoint_id": request.endpoint_id}

    def complete(self, request_id: str, success: bool = True) -> dict:
        request = self._processing.pop(request_id, None)
        if not request:
            raise ValueError(f"Request {request_id} not in processing")
        request.status = "completed" if success else "failed"
        self._completed.append(request)
        return {"request_id": request_id, "status": request.status}

    def get_stats(self) -> dict:
        completed = [r for r in self._completed if r.status == "completed"]
        failed = [r for r in self._completed if r.status == "failed"]
        return {
            "queued": len(self._queue),
            "processing": len(self._processing),
            "completed": len(completed),
            "failed": len(failed),
            "max_concurrent": self._max_concurrent,
            "utilization": round(len(self._processing) / self._max_concurrent * 100, 1),
        }

    def peek(self, count: int = 5) -> list[dict]:
        items = sorted(self._queue)[:count]
        return [{"request_id": r.request_id, "priority": r.priority,
                 "consumer_id": r.consumer_id} for _, _, r in items]

    def cancel(self, request_id: str) -> dict:
        for i, (p, c, r) in enumerate(self._queue):
            if r.request_id == request_id:
                self._queue.pop(i)
                heapq.heapify(self._queue)
                return {"cancelled": True, "request_id": request_id}
        return {"cancelled": False, "reason": "not_found"}

    def drain(self) -> list[dict]:
        """Dequeue all possible requests up to concurrency limit."""
        results = []
        while len(self._processing) < self._max_concurrent and self._queue:
            result = self.dequeue()
            if result and "error" not in result:
                results.append(result)
            else:
                break
        return results
