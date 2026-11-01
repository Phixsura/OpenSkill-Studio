"""Fleet GCP DM — track Deployment Manager status."""
from __future__ import annotations
def fleet_gcp_dm(deployments: list[dict]) -> dict:
    done = [d for d in deployments if d.get("status") == "DONE"]
    failed = [d for d in deployments if d.get("status") == "FAILED"]
    return {"total": len(deployments), "done": len(done), "failed": len(failed),
            "healthy": len(failed) == 0}
