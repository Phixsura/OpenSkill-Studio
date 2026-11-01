"""Fleet queue depth — monitor message queue depths across services."""
from __future__ import annotations
def fleet_queue_depth(queues: list[dict]) -> dict:
    total = sum(q.get("depth", 0) for q in queues)
    max_depth = max((q.get("depth", 0) for q in queues), default=0)
    return {"total_depth": total, "max_depth": max_depth,
            "queues": len(queues), "backlog": total > 10000}
