"""Fleet Canary Deploy v9 — track canary deployment progress and rollbacks."""
from __future__ import annotations
def fleet_canary_deploy_v9(deploys: list[dict]) -> dict:
    active = [d for d in deploys if d.get("phase") == "canary"]
    promoted = [d for d in deploys if d.get("phase") == "promoted"]
    rolled_back = [d for d in deploys if d.get("phase") == "rollback"]
    return {"total": len(deploys), "canary": len(active), "promoted": len(promoted),
            "rolled_back": len(rolled_back), "success_rate": round(len(promoted) / len(deploys) * 100, 1) if deploys else 0,
            "healthy": len(rolled_back) == 0}
