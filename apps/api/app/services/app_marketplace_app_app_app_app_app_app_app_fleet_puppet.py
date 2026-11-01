"""Fleet Puppet — track configuration enforcement."""
from __future__ import annotations
def fleet_puppet_status(nodes: list[dict]) -> dict:
    in_sync = [n for n in nodes if n.get("status") == "unchanged"]
    changed = [n for n in nodes if n.get("status") == "changed"]
    failed = [n for n in nodes if n.get("status") == "failed"]
    return {"total": len(nodes), "in_sync": len(in_sync), "changed": len(changed),
            "failed": len(failed), "converged": len(failed) == 0}
