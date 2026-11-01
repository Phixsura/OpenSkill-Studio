"""Queue manager — priority task queue with FIFO and priority modes."""

import html
from collections import deque
from datetime import datetime, timezone
import heapq


class TaskQueue:
    def __init__(self, *, max_size: int = 1000):
        self._queue: list[tuple[int, int, dict]] = []
        self._counter = 0
        self.max_size = max_size
        self.processed = 0

    def push(self, *, task: dict, priority: int = 0) -> dict:
        if len(self._queue) >= self.max_size:
            return {"error": "Queue full"}
        self._counter += 1
        entry = {"id": f"task_{self._counter}", "data": task,
                 "priority": priority, "status": "pending",
                 "created_at": datetime.now(timezone.utc).isoformat()}
        heapq.heappush(self._queue, (-priority, self._counter, entry))
        return entry

    def pop(self) -> dict | None:
        if not self._queue:
            return None
        _, _, entry = heapq.heappop(self._queue)
        entry["status"] = "processing"
        self.processed += 1
        return entry

    def stats(self) -> dict:
        return {"pending": len(self._queue), "processed": self.processed,
                "max_size": self.max_size,
                "utilization_pct": round(len(self._queue) / max(self.max_size, 1) * 100, 1)}
