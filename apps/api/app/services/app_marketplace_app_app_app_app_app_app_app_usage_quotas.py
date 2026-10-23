"""Platform usage quotas — enforce and track resource limits per plan."""
from __future__ import annotations

PLANS = {
    "free": {"api_calls": 1000, "storage_mb": 100, "apps": 3, "webhooks": 5},
    "starter": {"api_calls": 50000, "storage_mb": 5000, "apps": 10, "webhooks": 25},
    "pro": {"api_calls": 500000, "storage_mb": 50000, "apps": 50, "webhooks": 100},
    "enterprise": {"api_calls": -1, "storage_mb": -1, "apps": -1, "webhooks": -1},  # unlimited
}


def get_quotas(plan: str) -> dict:
    limits = PLANS.get(plan, PLANS["free"])
    return {"plan": plan, "limits": {k: "unlimited" if v == -1 else v for k, v in limits.items()}}


def check_usage(plan: str, usage: dict) -> dict:
    limits = PLANS.get(plan, PLANS["free"])
    checks = []
    any_exceeded = False
    for resource, limit in limits.items():
        used = usage.get(resource, 0)
        if limit == -1:
            checks.append({"resource": resource, "used": used, "limit": "unlimited",
                           "pct": 0, "exceeded": False})
        else:
            pct = round(used / max(limit, 1) * 100, 1)
            exceeded = used >= limit
            if exceeded:
                any_exceeded = True
            checks.append({"resource": resource, "used": used, "limit": limit,
                           "pct": pct, "exceeded": exceeded,
                           "warning": pct >= 80 and not exceeded})
    return {"plan": plan, "checks": checks, "any_exceeded": any_exceeded,
            "upgrade_suggested": any_exceeded and plan != "enterprise"}
