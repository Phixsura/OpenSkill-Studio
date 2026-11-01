"""Resource quota manager — enforce usage limits per tenant."""
from __future__ import annotations

QUOTAS = {
    "api_calls": {"free": 1000, "pro": 50000, "enterprise": -1},
    "storage_mb": {"free": 100, "pro": 5000, "enterprise": -1},
    "webhooks": {"free": 3, "pro": 25, "enterprise": -1},
    "team_members": {"free": 2, "pro": 10, "enterprise": -1},
    "apps": {"free": 1, "pro": 10, "enterprise": -1},
}


def get_quotas(plan: str) -> dict:
    result = {}
    for resource, limits in QUOTAS.items():
        limit = limits.get(plan, limits["free"])
        result[resource] = {"limit": limit, "unlimited": limit == -1}
    return {"plan": plan, "quotas": result}


def check_quota(plan: str, resource: str, current_usage: int) -> dict:
    if resource not in QUOTAS:
        return {"allowed": False, "reason": "unknown_resource"}
    limit = QUOTAS[resource].get(plan, QUOTAS[resource]["free"])
    if limit == -1:
        return {"allowed": True, "remaining": -1, "unlimited": True}
    remaining = max(0, limit - current_usage)
    return {"allowed": current_usage < limit, "remaining": remaining,
            "usage": current_usage, "limit": limit, "unlimited": False,
            "pct_used": round(current_usage / max(limit, 1) * 100)}
