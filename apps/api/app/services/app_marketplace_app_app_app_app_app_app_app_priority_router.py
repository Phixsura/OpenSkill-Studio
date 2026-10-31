"""Request priority router — route requests by priority class."""
from __future__ import annotations
from collections import defaultdict


class PriorityRouter:
    def __init__(self):
        self._queues: dict[str, list[dict]] = defaultdict(list)
        self._priorities = ["critical", "high", "normal", "low", "background"]
        self._processed = 0

    def enqueue(self, request_id: str, priority: str = "normal", payload: dict | None = None) -> dict:
        if priority not in self._priorities:
            priority = "normal"
        self._queues[priority].append({"id": request_id, "priority": priority, "payload": payload or {}})
        return {"id": request_id, "priority": priority, "queue_depth": len(self._queues[priority])}

    def dequeue(self) -> dict | None:
        for p in self._priorities:
            if self._queues[p]:
                item = self._queues[p].pop(0)
                self._processed += 1
                return item
        return None

    def stats(self) -> dict:
        depths = {p: len(self._queues[p]) for p in self._priorities}
        total = sum(depths.values())
        return {"total_queued": total, "depths": depths, "processed": self._processed}
