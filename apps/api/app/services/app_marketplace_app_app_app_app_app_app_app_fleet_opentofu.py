"""Fleet OpenTofu — track OpenTofu state and plan status."""
from __future__ import annotations
def fleet_opentofu_status(workspaces: list[dict]) -> dict:
    clean = [w for w in workspaces if w.get("plan_changes", 0) == 0]
    with_changes = [w for w in workspaces if w.get("plan_changes", 0) > 0]
    total_resources = sum(w.get("resources", 0) for w in workspaces)
    return {"total": len(workspaces), "clean": len(clean), "with_changes": len(with_changes),
            "total_resources": total_resources, "all_clean": len(clean) == len(workspaces)}
