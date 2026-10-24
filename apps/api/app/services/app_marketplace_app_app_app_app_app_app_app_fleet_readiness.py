"""Fleet readiness probe — aggregate readiness status."""
from __future__ import annotations
def fleet_readiness(endpoints: list[dict]) -> dict:
    ready = [e for e in endpoints if e.get("ready", False)]
    return {"ready": len(ready), "not_ready": len(endpoints) - len(ready),
            "total": len(endpoints), "all_ready": len(ready) == len(endpoints)}
