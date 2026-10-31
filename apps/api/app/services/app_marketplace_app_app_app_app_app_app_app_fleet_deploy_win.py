"""Fleet deployment window — track deployment time windows."""
from __future__ import annotations
def fleet_deploy_window(deploys: list[dict]) -> dict:
    in_window = [d for d in deploys if d.get("in_maintenance_window", False)]
    out_window = len(deploys) - len(in_window)
    return {"total": len(deploys), "in_window": len(in_window),
            "out_window": out_window, "compliant": out_window == 0}
