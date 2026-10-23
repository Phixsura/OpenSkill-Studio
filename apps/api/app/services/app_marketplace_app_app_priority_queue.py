"""Priority queue — multi-level priority task scheduler."""

from __future__ import annotations
import html
from collections import deque
from datetime import datetime, timezone

PRIORITY_LABELS = {0: "critical", 1: "high", 2: "medium", 3: "low"}


class MultiLevelQueue:
    def __init__(self):
        self._queues: dict[int, deque] = {i: deque() for i in range(4)}
        self._total_processed = 0

    def enqueue(self, *, task: dict, priority: int = 2) -> dict:
        p = max(0, min(3, priority))
        entry = {"id": f"task_{self._total_processed + len(self._queues[p]) + 1}",
                 "data": task, "priority": p,
                 "label": PRIORITY_LABELS[p],
                 "enqueued_at": datetime.now(timezone.utc).isoformat()}
        self._queues[p].append(entry)
        return entry

    def dequeue(self) -> dict | None:
        for p in range(4):
            if self._queues[p]:
                self._total_processed += 1
                return self._queues[p].popleft()
        return None

    def stats(self) -> dict:
        by_priority = {PRIORITY_LABELS[p]: len(q) for p, q in self._queues.items()}
        total = sum(by_priority.values())
        return {"pending": total, "by_priority": by_priority,
                "processed": self._total_processed,
                "has_critical": len(self._queues[0]) > 0}
