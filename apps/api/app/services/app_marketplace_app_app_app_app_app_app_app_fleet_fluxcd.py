"""Fleet FluxCD — track Flux reconciliation status."""
from __future__ import annotations
def fleet_fluxcd_status(resources: list[dict]) -> dict:
    ready = [r for r in resources if r.get("ready", False)]
    suspended = [r for r in resources if r.get("suspended", False)]
    return {"total": len(resources), "ready": len(ready), "not_ready": len(resources) - len(ready),
            "suspended": len(suspended), "all_ready": len(ready) == len(resources)}
