"""Fleet infrastructure drift — detect IaC drift."""
from __future__ import annotations
def fleet_infra_drift(resources: list[dict]) -> dict:
    drifted = [r for r in resources if r.get("drifted", False)]
    unmanaged = [r for r in resources if not r.get("managed", True)]
    return {"total": len(resources), "drifted": len(drifted),
            "unmanaged": len(unmanaged), "clean": len(drifted) == 0 and len(unmanaged) == 0}
