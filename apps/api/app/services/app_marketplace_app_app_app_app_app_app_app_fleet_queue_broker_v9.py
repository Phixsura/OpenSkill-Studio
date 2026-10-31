"""Fleet Queue Broker v9 — track message queue health and throughput."""
from __future__ import annotations
def fleet_queue_broker_v9(queues: list[dict]) -> dict:
    depth = sum(q.get("depth", 0) for q in queues)
    throughput = sum(q.get("msg_per_sec", 0) for q in queues)
    dlq = sum(q.get("dead_letters", 0) for q in queues)
    return {"queues": len(queues), "total_depth": depth, "throughput": throughput,
            "dead_letters": dlq, "healthy": dlq == 0}
