"""Fleet Terraform Cloud — track workspace run status."""
from __future__ import annotations
def fleet_tfc_status(workspaces: list[dict]) -> dict:
    applied = [w for w in workspaces if w.get("last_run") == "applied"]
    errored = [w for w in workspaces if w.get("last_run") == "errored"]
    cost_est = sum(w.get("monthly_cost_usd", 0) for w in workspaces)
    return {"total": len(workspaces), "applied": len(applied), "errored": len(errored),
            "monthly_cost": round(cost_est, 2), "healthy": len(errored) == 0}
