"""Fleet AI DR v5 — track ultimate disaster recovery."""
from __future__ import annotations
def fleet_ai_dr_v5(plans: list[dict]) -> dict:
    active = [p for p in plans if p.get("active", True)]
    rto_s = min((p.get("rto_s", 9999) for p in plans), default=9999)
    rpo_s = min((p.get("rpo_s", 9999) for p in plans), default=9999)
    drills = sum(p.get("drills_30d", 0) for p in plans)
    regions = sum(p.get("regions", 0) for p in plans)
    return {"plans": len(plans), "active": len(active), "rto_s": rto_s,
            "rpo_s": rpo_s, "drills": drills, "regions": regions, "instant": rto_s < 60}
