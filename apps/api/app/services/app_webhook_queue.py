"""Webhook delivery queue — manage pending webhook deliveries with priority."""

from collections import defaultdict
from datetime import UTC, datetime
import heapq


_queues: dict[str, list] = defaultdict(list)
_counter = 0


def enqueue_delivery(*, app_id: str, event_type: str, url: str, payload: dict, priority: int = 5) -> dict:
    """Enqueue a webhook delivery. Lower priority number = higher priority."""
    global _counter
    _counter += 1
    entry = {
        "id": f"whd_{_counter}",
        "app_id": app_id,
        "event_type": event_type,
        "url": url,
        "payload": payload,
        "priority": priority,
        "status": "queued",
        "queued_at": datetime.now(UTC).isoformat(),
    }
    heapq.heappush(_queues[app_id], (priority, _counter, entry))
    return entry


def dequeue_delivery(app_id: str) -> dict | None:
    """Get the highest priority delivery from the queue."""
    q = _queues.get(app_id, [])
    if not q:
        return None
    _, _, entry = heapq.heappop(q)
    return entry


def get_queue_size(app_id: str) -> int:
    return len(_queues.get(app_id, []))


def get_total_queued() -> int:
    return sum(len(q) for q in _queues.values())


def clear_queue(app_id: str) -> int:
    count = len(_queues.pop(app_id, []))
    return count
