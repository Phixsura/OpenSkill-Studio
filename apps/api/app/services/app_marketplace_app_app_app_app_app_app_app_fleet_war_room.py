"""Fleet war room — track active incident war rooms."""
from __future__ import annotations
def fleet_war_room(rooms: list[dict]) -> dict:
    active = [r for r in rooms if r.get("status") == "active"]
    avg_dur = round(sum(r.get("duration_min", 0) for r in rooms) / max(len(rooms), 1), 1)
    return {"total": len(rooms), "active": len(active), "resolved": len(rooms) - len(active),
            "avg_duration_min": avg_dur, "calm": len(active) == 0}
