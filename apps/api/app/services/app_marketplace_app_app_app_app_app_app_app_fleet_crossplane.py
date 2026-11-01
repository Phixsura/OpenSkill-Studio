"""Fleet Crossplane — track managed infrastructure resources."""
from __future__ import annotations
def fleet_crossplane_status(resources: list[dict]) -> dict:
    ready = [r for r in resources if r.get("condition") == "Ready"]
    synced = [r for r in resources if r.get("synced", False)]
    return {"total": len(resources), "ready": len(ready), "synced": len(synced),
            "not_ready": len(resources) - len(ready), "all_ready": len(ready) == len(resources)}
