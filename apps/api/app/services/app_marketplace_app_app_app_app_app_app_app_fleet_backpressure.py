"""Fleet backpressure — track queue backpressure signals."""
from __future__ import annotations
def fleet_backpressure(queues: list[dict]) -> dict:
    pressured = [q for q in queues if q.get("backpressure_active", False)]
    dropped = sum(q.get("dropped_messages", 0) for q in queues)
    return {"total": len(queues), "pressured": len(pressured), "dropped": dropped,
            "stable": len(pressured) == 0 and dropped == 0}
