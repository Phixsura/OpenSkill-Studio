"""Fleet Deployment History v9 — track deployment audit trail."""
from __future__ import annotations
def fleet_deployment_history_v9(deploys: list[dict]) -> dict:
    success = [d for d in deploys if d.get("result") == "success"]
    rollbacks = [d for d in deploys if d.get("result") == "rollback"]
    envs = len({d.get("env") for d in deploys if d.get("env")})
    return {"total": len(deploys), "success": len(success), "rollbacks": len(rollbacks),
            "environments": envs, "healthy": len(rollbacks) < len(deploys) * 0.05}
