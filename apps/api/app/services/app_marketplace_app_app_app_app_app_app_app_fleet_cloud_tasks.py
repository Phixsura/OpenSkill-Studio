"""Fleet Cloud Tasks — track distributed task queue."""
from __future__ import annotations
def fleet_cloud_tasks(queues: list[dict]) -> dict:
    active = [q for q in queues if q.get("state") == "RUNNING"]
    tasks_24h = sum(q.get("dispatched_24h", 0) for q in queues)
    success_rate = round(sum(q.get("success_rate", 100) for q in queues) / max(len(queues), 1), 1)
    return {"queues": len(queues), "active": len(active), "tasks_24h": tasks_24h,
            "success_rate": success_rate, "reliable": success_rate >= 99}
