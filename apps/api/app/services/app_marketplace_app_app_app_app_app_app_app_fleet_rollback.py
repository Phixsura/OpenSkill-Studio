"""Fleet rollback tracker — track rollback events."""
from __future__ import annotations
def fleet_rollback_stats(events: list[dict]) -> dict:
    auto = [e for e in events if e.get("type") == "auto"]
    manual = [e for e in events if e.get("type") == "manual"]
    return {"total": len(events), "auto": len(auto), "manual": len(manual),
            "rollback_rate": round(len(events) / max(1, 1) * 100, 1) if events else 0}
