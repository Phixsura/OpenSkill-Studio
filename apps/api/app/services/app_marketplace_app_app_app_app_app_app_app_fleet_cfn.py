"""Fleet CloudFormation — track CFN stack status."""
from __future__ import annotations
def fleet_cfn_status(stacks: list[dict]) -> dict:
    complete = [s for s in stacks if "COMPLETE" in s.get("status", "") and "ROLLBACK" not in s.get("status", "")]
    rollback = [s for s in stacks if "ROLLBACK" in s.get("status", "")]
    in_progress = [s for s in stacks if "IN_PROGRESS" in s.get("status", "")]
    return {"total": len(stacks), "complete": len(complete), "rollback": len(rollback),
            "in_progress": len(in_progress), "healthy": len(rollback) == 0}
