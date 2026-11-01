"""Fleet Tekton — track cloud-native CI/CD pipeline runs."""
from __future__ import annotations
def fleet_tekton_status(runs: list[dict]) -> dict:
    succeeded = [r for r in runs if r.get("status") == "Succeeded"]
    failed = [r for r in runs if r.get("status") == "Failed"]
    running = [r for r in runs if r.get("status") == "Running"]
    avg_dur = round(sum(r.get("duration_min", 0) for r in succeeded) / max(len(succeeded), 1), 1)
    return {"total": len(runs), "succeeded": len(succeeded), "failed": len(failed),
            "running": len(running), "avg_duration_min": avg_dur}
