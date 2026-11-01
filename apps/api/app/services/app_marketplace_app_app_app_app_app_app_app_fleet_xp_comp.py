"""Fleet Crossplane compositions — track XR/composition health."""
from __future__ import annotations
def fleet_xp_compositions(compositions: list[dict]) -> dict:
    ready = [c for c in compositions if c.get("ready", True)]
    resources = sum(c.get("managed_resources", 0) for c in compositions)
    return {"total": len(compositions), "ready": len(ready), "not_ready": len(compositions) - len(ready),
            "managed_resources": resources, "all_ready": len(ready) == len(compositions)}
