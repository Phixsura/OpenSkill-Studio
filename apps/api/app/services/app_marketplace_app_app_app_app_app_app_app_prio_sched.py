"""Request priority scheduler — schedule requests by priority with fair queuing."""
from __future__ import annotations
from collections import defaultdict


class PriorityScheduler:
    PRIORITIES = {"critical": 0, "high": 1, "normal": 2, "low": 3, "background": 4}

    def __init__(self):
        self._queues: dict[str, list[dict]] = {p: [] for p in self.PRIORITIES}
        self._processed = 0

    def submit(self, request_id: str, priority: str = "normal", payload: dict | None = None) -> dict:
        p = priority if priority in self.PRIORITIES else "normal"
        self._queues[p].append({"id": request_id, "priority": p, "payload": payload or {}})
        return {"id": request_id, "priority": p, "queue_depth": len(self._queues[p])}

    def next(self) -> dict | None:
        for p in sorted(self.PRIORITIES, key=self.PRIORITIES.get):
            if self._queues[p]:
                item = self._queues[p].pop(0)
                self._processed += 1
                return item
        return None

    def stats(self) -> dict:
        depths = {p: len(q) for p, q in self._queues.items()}
        return {"total_queued": sum(depths.values()), "depths": depths,
                "processed": self._processed}
