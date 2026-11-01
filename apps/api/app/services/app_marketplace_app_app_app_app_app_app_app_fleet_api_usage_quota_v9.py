"""Fleet API Usage Quota v9 — track per-consumer API usage quotas."""
from __future__ import annotations
def fleet_api_usage_quota_v9(consumers: list[dict]) -> dict:
    over_quota = [c for c in consumers if c.get("usage_pct", 0) > 100]
    near_quota = [c for c in consumers if 80 < c.get("usage_pct", 0) <= 100]
    total_calls = sum(c.get("calls_today", 0) for c in consumers)
    return {"consumers": len(consumers), "over_quota": len(over_quota), "near_quota": len(near_quota),
            "calls_today": total_calls, "healthy": len(over_quota) == 0}
