"""Fleet Step Functions — track state machine execution."""
from __future__ import annotations
def fleet_stepfn_status(machines: list[dict]) -> dict:
    active = [m for m in machines if m.get("status") == "ACTIVE"]
    running_exec = sum(m.get("running_executions", 0) for m in machines)
    succeeded = sum(m.get("succeeded_24h", 0) for m in machines)
    failed = sum(m.get("failed_24h", 0) for m in machines)
    return {"machines": len(machines), "active": len(active), "running": running_exec,
            "succeeded_24h": succeeded, "failed_24h": failed, "healthy": failed == 0}
