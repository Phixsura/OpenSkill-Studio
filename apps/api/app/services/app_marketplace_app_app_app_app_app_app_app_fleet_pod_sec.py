"""Fleet pod security — track pod security standards compliance."""
from __future__ import annotations
def fleet_pod_security(pods: list[dict]) -> dict:
    privileged = [p for p in pods if p.get("privileged", False)]
    root = [p for p in pods if p.get("run_as_root", False)]
    return {"total": len(pods), "privileged": len(privileged), "run_as_root": len(root),
            "compliant": len(privileged) == 0 and len(root) == 0}
