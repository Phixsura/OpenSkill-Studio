"""Fleet BullMQ — track Node.js queue processing."""
from __future__ import annotations
def fleet_bullmq_status(queues: list[dict]) -> dict:
    total_waiting = sum(q.get("waiting", 0) for q in queues)
    total_active = sum(q.get("active", 0) for q in queues)
    total_completed = sum(q.get("completed_24h", 0) for q in queues)
    total_failed = sum(q.get("failed_24h", 0) for q in queues)
    return {"queues": len(queues), "waiting": total_waiting, "active": total_active,
            "completed_24h": total_completed, "failed_24h": total_failed, "healthy": total_failed == 0}
