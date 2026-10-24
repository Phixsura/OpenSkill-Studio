"""Request queue manager — priority queue with dead letter support."""
from __future__ import annotations
import time


class RequestQueue:
    def __init__(self, max_retries: int = 3):
        self._queue: list[dict] = []
        self._dlq: list[dict] = []
        self._processed = 0
        self._max_retries = max_retries

    def enqueue(self, request_id: str, payload: dict, priority: int = 0) -> dict:
        item = {"id": request_id, "payload": payload, "priority": priority,
                "attempts": 0, "enqueued_at": time.time()}
        self._queue.append(item)
        self._queue.sort(key=lambda x: -x["priority"])
        return {"id": request_id, "position": self._queue.index(item) + 1, "queue_size": len(self._queue)}

    def dequeue(self) -> dict | None:
        if not self._queue:
            return None
        item = self._queue.pop(0)
        item["attempts"] += 1
        return item

    def nack(self, item: dict, error: str) -> dict:
        if item["attempts"] >= self._max_retries:
            item["last_error"] = error
            self._dlq.append(item)
            return {"action": "dead_lettered", "id": item["id"]}
        self._queue.append(item)
        return {"action": "requeued", "id": item["id"], "attempt": item["attempts"]}

    def ack(self, item: dict) -> dict:
        self._processed += 1
        return {"action": "acknowledged", "id": item["id"]}

    def stats(self) -> dict:
        return {"queue_size": len(self._queue), "dlq_size": len(self._dlq),
                "processed": self._processed, "max_retries": self._max_retries}
