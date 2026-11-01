"""Fleet Ansible — track configuration management runs."""
from __future__ import annotations
def fleet_ansible_status(runs: list[dict]) -> dict:
    ok = [r for r in runs if r.get("status") == "ok"]
    changed = [r for r in runs if r.get("status") == "changed"]
    failed = [r for r in runs if r.get("status") == "failed"]
    return {"total": len(runs), "ok": len(ok), "changed": len(changed),
            "failed": len(failed), "idempotent": len(changed) == 0 and len(failed) == 0}
