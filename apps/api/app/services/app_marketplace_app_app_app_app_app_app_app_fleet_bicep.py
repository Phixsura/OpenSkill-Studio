"""Fleet Azure Bicep — track Bicep deployment status."""
from __future__ import annotations
def fleet_bicep_status(deployments: list[dict]) -> dict:
    succeeded = [d for d in deployments if d.get("status") == "Succeeded"]
    failed = [d for d in deployments if d.get("status") == "Failed"]
    return {"total": len(deployments), "succeeded": len(succeeded), "failed": len(failed),
            "healthy": len(failed) == 0}
