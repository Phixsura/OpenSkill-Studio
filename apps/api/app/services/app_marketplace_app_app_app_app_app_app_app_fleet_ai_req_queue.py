"""Fleet AI Request Queue — track AI inference request queuing and priority."""
from __future__ import annotations
def fleet_ai_request_queue(queues: list[dict]) -> dict:
    active = [q for q in queues if q.get("active", True)]
    depth = sum(q.get("depth", 0) for q in queues)
    throughput = sum(q.get("throughput_rps", 0) for q in queues)
    avg_wait_ms = round(sum(q.get("avg_wait_ms", 0) for q in queues) / max(len(queues), 1), 1)
    return {"queues": len(queues), "active": len(active), "depth": depth,
            "throughput_rps": throughput, "avg_wait_ms": avg_wait_ms, "fast": avg_wait_ms < 100}
