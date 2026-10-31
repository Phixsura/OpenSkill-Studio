"""Fleet AI Priority Queue — track priority-based AI request scheduling."""
from __future__ import annotations
def fleet_ai_priority_queue(queues: list[dict]) -> dict:
    active = [q for q in queues if q.get("active", True)]
    levels = max((q.get("levels", 0) for q in queues), default=0)
    promoted_24h = sum(q.get("promoted", 0) for q in queues)
    total_24h = sum(q.get("total_24h", 0) for q in queues)
    return {"queues": len(queues), "active": len(active), "levels": levels,
            "promoted_24h": promoted_24h, "total_24h": total_24h, "prioritized": levels > 1}
