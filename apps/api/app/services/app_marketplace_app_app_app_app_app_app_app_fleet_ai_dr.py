"""Fleet AI Disaster Recovery — track AI infrastructure DR capabilities."""
from __future__ import annotations
def fleet_ai_disaster_recovery(plans: list[dict]) -> dict:
    active = [p for p in plans if p.get("active", True)]
    rto_min = min((p.get("rto_min", 9999) for p in plans), default=9999)
    rpo_min = min((p.get("rpo_min", 9999) for p in plans), default=9999)
    last_drill_days = min((p.get("last_drill_days", 9999) for p in plans), default=9999)
    return {"plans": len(plans), "active": len(active), "rto_min": rto_min,
            "rpo_min": rpo_min, "last_drill_days": last_drill_days, "prepared": last_drill_days < 30}
