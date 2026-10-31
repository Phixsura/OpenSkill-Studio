"""Fleet AI Platform DR v2 — track disaster recovery at platform scale."""
from __future__ import annotations
def fleet_ai_platform_dr_v2(plans: list[dict]) -> dict:
    active = [p for p in plans if p.get("active", True)]
    rto_min = min((p.get("rto_min", 9999) for p in plans), default=9999)
    rpo_min = min((p.get("rpo_min", 9999) for p in plans), default=9999)
    drills_30d = sum(p.get("drills", 0) for p in plans)
    regions = sum(p.get("regions", 0) for p in plans)
    return {"plans": len(plans), "active": len(active), "rto_min": rto_min,
            "rpo_min": rpo_min, "drills_30d": drills_30d, "regions": regions, "prepared": drills_30d > 0}
