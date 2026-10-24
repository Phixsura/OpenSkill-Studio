"""Fleet Thanos — track global query view health."""
from __future__ import annotations
def fleet_thanos_status(stores: list[dict]) -> dict:
    healthy = [s for s in stores if s.get("healthy", True)]
    compaction_ok = [s for s in stores if not s.get("compaction_behind", False)]
    return {"stores": len(stores), "healthy": len(healthy),
            "compaction_ok": len(compaction_ok), "all_healthy": len(healthy) == len(stores)}
