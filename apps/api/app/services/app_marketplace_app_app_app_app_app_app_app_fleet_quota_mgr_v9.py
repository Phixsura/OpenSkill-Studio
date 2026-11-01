"""Fleet Quota Manager v9 — track resource quota enforcement per tenant."""
from __future__ import annotations
def fleet_quota_mgr_v9(tenants: list[dict]) -> dict:
    over_quota = [t for t in tenants if t.get("usage_pct", 0) > 100]
    near_limit = [t for t in tenants if 80 < t.get("usage_pct", 0) <= 100]
    avg_usage = sum(t.get("usage_pct", 0) for t in tenants) / len(tenants) if tenants else 0
    return {"tenants": len(tenants), "over_quota": len(over_quota), "near_limit": len(near_limit),
            "avg_usage_pct": round(avg_usage, 1), "healthy": len(over_quota) == 0}
