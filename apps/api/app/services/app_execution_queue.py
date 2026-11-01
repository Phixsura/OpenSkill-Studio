"""Sandbox execution queue — manage pending and running executions.

In-memory queue for tracking sandbox execution status,
with concurrency limiting per app.
"""

from collections import defaultdict
from datetime import UTC, datetime


_queues: dict[str, list[dict]] = defaultdict(list)
_running: dict[str, int] = defaultdict(int)

DEFAULT_MAX_CONCURRENT = 5


def enqueue_execution(
    *,
    app_id: str,
    installation_id: str,
    function_name: str,
    payload: dict,
) -> dict:
    """Add an execution to the queue."""
    entry = {
        "id": f"exec_{app_id}_{len(_queues[app_id])}_{int(datetime.now(UTC).timestamp())}",
        "app_id": app_id,
        "installation_id": installation_id,
        "function_name": function_name,
        "payload": payload,
        "status": "queued",
        "queued_at": datetime.now(UTC).isoformat(),
    }
    _queues[app_id].append(entry)
    return entry


def can_execute(app_id: str, max_concurrent: int = DEFAULT_MAX_CONCURRENT) -> bool:
    """Check if an app has capacity for another execution."""
    return _running.get(app_id, 0) < max_concurrent


def start_execution(app_id: str) -> None:
    """Mark an execution as started (increment running count)."""
    _running[app_id] = _running.get(app_id, 0) + 1


def finish_execution(app_id: str) -> None:
    """Mark an execution as finished (decrement running count)."""
    _running[app_id] = max(0, _running.get(app_id, 0) - 1)


def get_queue_depth(app_id: str) -> int:
    """Get number of queued executions for an app."""
    return len([e for e in _queues.get(app_id, []) if e["status"] == "queued"])


def get_running_count(app_id: str) -> int:
    """Get number of running executions."""
    return _running.get(app_id, 0)
