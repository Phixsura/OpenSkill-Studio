"""API rate quota dashboard — unified view of all rate limits and quotas."""
from __future__ import annotations


def build_quota_dashboard(quotas: list[dict]) -> dict:
    results = []
    at_risk = 0
    exhausted = 0
    for q in quotas:
        used = q.get("used", 0)
        limit = q.get("limit", 1)
        pct = round(used / max(limit, 1) * 100, 1)
        status = "exhausted" if pct >= 100 else "at_risk" if pct >= 80 else "healthy"
        if status == "at_risk":
            at_risk += 1
        elif status == "exhausted":
            exhausted += 1
        results.append({"name": q["name"], "used": used, "limit": limit,
                         "pct_used": pct, "status": status,
                         "remaining": max(0, limit - used)})
    return {"quotas": results, "total": len(results), "at_risk": at_risk,
            "exhausted": exhausted, "healthy": len(results) - at_risk - exhausted}
