"""Fleet API Rate Plan v9 — track API pricing tier rate limits."""
from __future__ import annotations
def fleet_api_rate_plan_v9(plans: list[dict]) -> dict:
    active = [p for p in plans if p.get("active")]
    subscribers = sum(p.get("subscribers", 0) for p in plans)
    total_quota = sum(p.get("monthly_quota", 0) for p in plans)
    return {"plans": len(plans), "active": len(active), "subscribers": subscribers,
            "total_monthly_quota": total_quota, "healthy": True}
