"""Fleet Kustomize — track overlay consistency."""
from __future__ import annotations
def fleet_kustomize_status(overlays: list[dict]) -> dict:
    valid = [o for o in overlays if o.get("valid", True)]
    stale = [o for o in overlays if o.get("stale", False)]
    return {"total": len(overlays), "valid": len(valid), "invalid": len(overlays) - len(valid),
            "stale": len(stale), "clean": len(stale) == 0 and len(valid) == len(overlays)}
