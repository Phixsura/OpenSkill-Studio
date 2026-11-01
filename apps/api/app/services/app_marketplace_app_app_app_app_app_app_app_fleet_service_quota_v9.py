"""Fleet Service Quota v9 — track cloud service quota utilization."""
from __future__ import annotations
def fleet_service_quota_v9(quotas: list[dict]) -> dict:
    near_limit = [q for q in quotas if q.get("usage_pct", 0) > 80]
    at_limit = [q for q in quotas if q.get("usage_pct", 0) >= 100]
    avg_usage = sum(q.get("usage_pct", 0) for q in quotas) / len(quotas) if quotas else 0
    return {"quotas": len(quotas), "near_limit": len(near_limit), "at_limit": len(at_limit),
            "avg_usage_pct": round(avg_usage, 1), "healthy": len(at_limit) == 0}
