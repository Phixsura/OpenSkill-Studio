"""Fleet AWS CDK — track CDK stack deployment status."""
from __future__ import annotations
def fleet_cdk_status(stacks: list[dict]) -> dict:
    deployed = [s for s in stacks if s.get("status") == "CREATE_COMPLETE" or s.get("status") == "UPDATE_COMPLETE"]
    failed = [s for s in stacks if "FAILED" in s.get("status", "")]
    drifted = [s for s in stacks if s.get("drift_detected", False)]
    return {"total": len(stacks), "deployed": len(deployed), "failed": len(failed),
            "drifted": len(drifted), "healthy": len(failed) == 0 and len(drifted) == 0}
