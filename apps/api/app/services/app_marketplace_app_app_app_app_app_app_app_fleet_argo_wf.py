"""Fleet Argo Workflows — track workflow execution metrics."""
from __future__ import annotations
def fleet_argo_workflows(workflows: list[dict]) -> dict:
    succeeded = [w for w in workflows if w.get("phase") == "Succeeded"]
    failed = [w for w in workflows if w.get("phase") == "Failed"]
    running = [w for w in workflows if w.get("phase") == "Running"]
    avg_dur = round(sum(w.get("duration_min", 0) for w in succeeded) / max(len(succeeded), 1), 1)
    return {"total": len(workflows), "succeeded": len(succeeded), "failed": len(failed),
            "running": len(running), "avg_duration_min": avg_dur}
