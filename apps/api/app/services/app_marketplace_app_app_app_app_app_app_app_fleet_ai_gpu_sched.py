"""Fleet AI GPU Scheduler — track GPU workload scheduling and sharing."""
from __future__ import annotations
def fleet_ai_gpu_scheduler(schedulers: list[dict]) -> dict:
    active = [s for s in schedulers if s.get("active", True)]
    gpus = sum(s.get("gpus", 0) for s in schedulers)
    jobs_queued = sum(s.get("queued", 0) for s in schedulers)
    utilization = round(sum(s.get("util_pct", 0) for s in schedulers) / max(len(schedulers), 1), 1)
    sharing = all(s.get("mig_enabled", False) for s in schedulers)
    return {"schedulers": len(schedulers), "active": len(active), "gpus": gpus,
            "queued": jobs_queued, "utilization": utilization, "sharing": sharing}
