"""Fleet AI Dead Letter Queue — track failed AI message handling."""
from __future__ import annotations
def fleet_ai_dlq(queues: list[dict]) -> dict:
    active = [q for q in queues if q.get("active", True)]
    messages = sum(q.get("messages", 0) for q in queues)
    retried = sum(q.get("retried", 0) for q in queues)
    discarded = sum(q.get("discarded", 0) for q in queues)
    return {"queues": len(queues), "active": len(active), "messages": messages,
            "retried": retried, "discarded": discarded, "clean": messages < 100}
