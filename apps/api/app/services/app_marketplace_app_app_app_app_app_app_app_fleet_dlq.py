"""Fleet DLQ — track dead letter queue depths."""
from __future__ import annotations
def fleet_dlq_status(queues: list[dict]) -> dict:
    total_msgs = sum(q.get("messages", 0) for q in queues)
    non_empty = [q for q in queues if q.get("messages", 0) > 0]
    return {"queues": len(queues), "total_messages": total_msgs,
            "non_empty": len(non_empty), "clean": total_msgs == 0}
