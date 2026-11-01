"""Fleet Terraform state — track IaC state health."""
from __future__ import annotations
def fleet_tf_state(workspaces: list[dict]) -> dict:
    healthy = [w for w in workspaces if w.get("state_locked", False) is False and w.get("last_apply_ok", True)]
    locked = [w for w in workspaces if w.get("state_locked", False)]
    failed = [w for w in workspaces if not w.get("last_apply_ok", True)]
    return {"total": len(workspaces), "healthy": len(healthy), "locked": len(locked),
            "failed": len(failed), "all_ok": len(locked) == 0 and len(failed) == 0}
