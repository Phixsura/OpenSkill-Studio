"""Fleet Task Queue v9 — track async task execution and worker pools."""
from __future__ import annotations
def fleet_task_queue_v9(queues: list[dict]) -> dict:
    pending = sum(q.get("pending", 0) for q in queues)
    processing = sum(q.get("processing", 0) for q in queues)
    workers = sum(q.get("workers", 0) for q in queues)
    failed = sum(q.get("failed", 0) for q in queues)
    return {"queues": len(queues), "pending": pending, "processing": processing,
            "workers": workers, "failed": failed, "healthy": failed == 0}
