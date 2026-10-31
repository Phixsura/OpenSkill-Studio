"""Fleet AI Storage v8 — track ultimate distributed storage."""
from __future__ import annotations
def fleet_ai_storage_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    total_eb = round(sum(s.get("total_eb", 0) for s in systems), 1)
    iops = sum(s.get("iops", 0) for s in systems)
    durability = round(sum(s.get("durability", 0) for s in systems) / max(len(systems), 1), 6)
    return {"systems": len(systems), "active": len(active), "total_eb": total_eb,
            "iops": iops, "durability": durability, "enterprise": durability > 99.999}
