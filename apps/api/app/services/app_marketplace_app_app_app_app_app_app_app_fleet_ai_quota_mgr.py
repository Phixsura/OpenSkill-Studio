"""Fleet AI Quota Manager — track per-tenant AI resource quotas."""
from __future__ import annotations
def fleet_ai_quota_manager(quotas: list[dict]) -> dict:
    active = [q for q in quotas if q.get("active", True)]
    tenants = sum(q.get("tenants", 0) for q in quotas)
    enforced = sum(q.get("enforced", 0) for q in quotas)
    throttled_24h = sum(q.get("throttled_24h", 0) for q in quotas)
    return {"quotas": len(quotas), "active": len(active), "tenants": tenants,
            "enforced": enforced, "throttled_24h": throttled_24h, "fair": enforced == tenants}
