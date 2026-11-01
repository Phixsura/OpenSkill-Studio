"""Fleet queue wait time — track request queue wait times."""
from __future__ import annotations
def fleet_queue_wait(services: list[dict]) -> dict:
    avg_wait = round(sum(s.get("avg_wait_ms", 0) for s in services) / max(len(services), 1), 1)
    p99_wait = max((s.get("p99_wait_ms", 0) for s in services), default=0)
    return {"services": len(services), "avg_wait_ms": avg_wait, "p99_wait_ms": p99_wait,
            "acceptable": p99_wait < 5000}
