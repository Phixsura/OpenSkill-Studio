"""Fleet AI Storage v4 — track AI platform distributed storage."""
from __future__ import annotations
def fleet_ai_storage_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    total_pb = round(sum(s.get("total_pb", 0) for s in systems), 1)
    used_pb = round(sum(s.get("used_pb", 0) for s in systems), 1)
    iops = sum(s.get("iops", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "total_pb": total_pb,
            "used_pb": used_pb, "iops": iops, "available": total_pb > used_pb}
