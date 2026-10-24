"""Fleet SQS — track message queue health."""
from __future__ import annotations
def fleet_sqs_status(queues: list[dict]) -> dict:
    total_msgs = sum(q.get("messages_visible", 0) for q in queues)
    total_inflight = sum(q.get("messages_in_flight", 0) for q in queues)
    dlq_msgs = sum(q.get("dlq_messages", 0) for q in queues)
    return {"queues": len(queues), "visible": total_msgs, "in_flight": total_inflight,
            "dlq_messages": dlq_msgs, "clean": dlq_msgs == 0}
