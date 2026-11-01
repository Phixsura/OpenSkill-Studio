"""Fleet multi-region failover — track failover readiness."""
from __future__ import annotations
def fleet_failover_status(regions: list[dict]) -> dict:
    primary = [r for r in regions if r.get("role") == "primary"]
    standby = [r for r in regions if r.get("role") == "standby"]
    ready = [r for r in standby if r.get("ready", False)]
    return {"regions": len(regions), "primary": len(primary), "standby": len(standby),
            "standby_ready": len(ready), "failover_ready": len(ready) > 0}
