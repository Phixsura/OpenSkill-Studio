"""Webhook queue manager — manage webhook delivery queues."""
from __future__ import annotations


class WebhookQueueManager:
    def __init__(self, max_queue_size: int = 10000):
        self._queues: dict[str, list[dict]] = {}
        self._max = max_queue_size
        self._processed = 0

    def enqueue(self, subscriber_id: str, event: dict) -> dict:
        self._queues.setdefault(subscriber_id, [])
        if len(self._queues[subscriber_id]) >= self._max:
            return {"enqueued": False, "reason": "queue_full"}
        self._queues[subscriber_id].append(event)
        return {"enqueued": True, "queue_depth": len(self._queues[subscriber_id])}

    def dequeue(self, subscriber_id: str, batch_size: int = 10) -> dict:
        queue = self._queues.get(subscriber_id, [])
        batch = queue[:batch_size]
        self._queues[subscriber_id] = queue[batch_size:]
        self._processed += len(batch)
        return {"events": batch, "count": len(batch), "remaining": len(self._queues.get(subscriber_id, []))}

    def stats(self) -> dict:
        total_queued = sum(len(q) for q in self._queues.values())
        return {"subscribers": len(self._queues), "total_queued": total_queued,
                "processed": self._processed, "max_queue_size": self._max}
