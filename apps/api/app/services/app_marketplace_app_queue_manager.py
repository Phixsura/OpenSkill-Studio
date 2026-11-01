"""Queue manager — manage message queues for async app processing."""

from datetime import datetime, timezone
from collections import deque


class AppQueue:
    def __init__(self, *, max_size: int = 1000) -> None:
        self._queue: deque = deque(maxlen=max_size)
        self._processed = 0
        self._failed = 0

    def enqueue(self, message: dict) -> dict:
        entry = {**message, "enqueued_at": datetime.now(timezone.utc).isoformat()}
        self._queue.append(entry)
        return {"queued": True, "queue_size": len(self._queue)}

    def dequeue(self) -> dict | None:
        if not self._queue:
            return None
        msg = self._queue.popleft()
        self._processed += 1
        return msg

    def peek(self) -> dict | None:
        return self._queue[0] if self._queue else None

    def stats(self) -> dict:
        return {"size": len(self._queue), "processed": self._processed,
                "failed": self._failed, "max_size": self._queue.maxlen}
