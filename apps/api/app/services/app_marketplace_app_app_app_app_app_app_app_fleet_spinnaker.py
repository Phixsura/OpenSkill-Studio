"""Fleet Spinnaker — track multi-cloud deployment pipelines."""
from __future__ import annotations
def fleet_spinnaker_status(pipelines: list[dict]) -> dict:
    succeeded = [p for p in pipelines if p.get("status") == "SUCCEEDED"]
    failed = [p for p in pipelines if p.get("status") == "TERMINAL"]
    running = [p for p in pipelines if p.get("status") == "RUNNING"]
    return {"total": len(pipelines), "succeeded": len(succeeded), "failed": len(failed),
            "running": len(running), "success_rate": round(len(succeeded) / max(len(pipelines), 1) * 100, 1)}
