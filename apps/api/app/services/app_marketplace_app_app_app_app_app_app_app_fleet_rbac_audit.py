"""Fleet RBAC audit — check for overprivileged service accounts."""
from __future__ import annotations
def fleet_rbac_audit(accounts: list[dict]) -> dict:
    overprivileged = [a for a in accounts if a.get("cluster_admin", False)]
    no_limits = [a for a in accounts if not a.get("has_resource_limits", True)]
    return {"total": len(accounts), "overprivileged": len(overprivileged),
            "no_limits": len(no_limits), "compliant": len(overprivileged) == 0}
