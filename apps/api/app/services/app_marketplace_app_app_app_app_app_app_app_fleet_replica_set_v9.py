"""Fleet Replica Set v9 — track desired vs actual replica counts."""
from __future__ import annotations
def fleet_replica_set_v9(sets: list[dict]) -> dict:
    desired = sum(s.get("desired", 0) for s in sets)
    ready = sum(s.get("ready", 0) for s in sets)
    unavailable = sum(s.get("unavailable", 0) for s in sets)
    return {"sets": len(sets), "desired": desired, "ready": ready,
            "unavailable": unavailable, "healthy": unavailable == 0}
