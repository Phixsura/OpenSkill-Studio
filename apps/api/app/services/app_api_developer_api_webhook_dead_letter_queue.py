"""App API Developer Webhook Dead Letter Queue — manage failed webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class DeadLetter:
    letter_id: str
    event_type: str
    destination: str
    payload_preview: str
    failure_reason: str
    retry_count: int
    created_at: float = field(default_factory=time.time)
    requeued: bool = False

class AppAPIDeveloperAPIWebhookDeadLetterQueue:
    def __init__(self, max_size: int = 5000) -> None:
        self._max = max(1, max_size)
        self._queue: dict[str, list[DeadLetter]] = {}

    def enqueue(self, installation_id: str, letter_id: str, event_type: str, destination: str, payload_preview: str, failure_reason: str, retry_count: int) -> DeadLetter:
        if not installation_id: raise ValueError("installation_id is required")
        dl = DeadLetter(letter_id=letter_id, event_type=event_type, destination=destination, payload_preview=payload_preview[:500], failure_reason=failure_reason, retry_count=retry_count)
        q = self._queue.setdefault(installation_id, [])
        q.append(dl)
        if len(q) > self._max: self._queue[installation_id] = q[-self._max:]
        return dl

    def peek(self, installation_id: str, limit: int = 20) -> list[DeadLetter]:
        return list(reversed(self._queue.get(installation_id, [])[-limit:]))

    def requeue(self, installation_id: str, letter_id: str) -> DeadLetter:
        for dl in self._queue.get(installation_id, []):
            if dl.letter_id == letter_id:
                dl.requeued = True
                return dl
        raise KeyError(f"Letter {letter_id} not found")

    def purge(self, installation_id: str, destination: str | None = None) -> int:
        q = self._queue.get(installation_id, [])
        if destination:
            before = len(q)
            self._queue[installation_id] = [dl for dl in q if dl.destination != destination]
            return before - len(self._queue[installation_id])
        count = len(q)
        self._queue[installation_id] = []
        return count

    def count(self, installation_id: str) -> int:
        return len(self._queue.get(installation_id, []))

    def by_destination(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for dl in self._queue.get(installation_id, []):
            counts[dl.destination] = counts.get(dl.destination, 0) + 1
        return counts
