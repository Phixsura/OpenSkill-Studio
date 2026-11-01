"""Fleet Sidekiq — track Ruby background job processing."""
from __future__ import annotations
def fleet_sidekiq_status(processes: list[dict]) -> dict:
    busy = sum(p.get("busy", 0) for p in processes)
    enqueued = sum(p.get("enqueued", 0) for p in processes)
    dead = sum(p.get("dead", 0) for p in processes)
    return {"processes": len(processes), "busy": busy, "enqueued": enqueued,
            "dead": dead, "healthy": dead == 0}
