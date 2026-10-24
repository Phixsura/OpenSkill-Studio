"""Fleet Celery — track distributed task queue health."""
from __future__ import annotations
def fleet_celery_status(workers: list[dict]) -> dict:
    online = [w for w in workers if w.get("status") == "online"]
    active_tasks = sum(w.get("active", 0) for w in workers)
    reserved = sum(w.get("reserved", 0) for w in workers)
    return {"workers": len(workers), "online": len(online), "active_tasks": active_tasks,
            "reserved": reserved, "all_online": len(online) == len(workers)}
