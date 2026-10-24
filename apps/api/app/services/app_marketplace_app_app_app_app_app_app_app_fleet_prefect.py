"""Fleet Prefect — track workflow orchestration health."""
from __future__ import annotations
def fleet_prefect_status(deployments: list[dict]) -> dict:
    active = [d for d in deployments if d.get("is_schedule_active", True)]
    completed_24h = sum(d.get("completed_24h", 0) for d in deployments)
    failed_24h = sum(d.get("failed_24h", 0) for d in deployments)
    return {"deployments": len(deployments), "active": len(active), "completed_24h": completed_24h,
            "failed_24h": failed_24h, "reliable": failed_24h == 0}
