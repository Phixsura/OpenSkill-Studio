"""Usage limit enforcer — enforce plan limits and show upgrade prompts."""
from __future__ import annotations

PLAN_LIMITS = {
    "free": {"apps": 3, "api_calls_daily": 1000, "webhooks": 5, "team_members": 1, "storage_mb": 100},
    "starter": {"apps": 10, "api_calls_daily": 50000, "webhooks": 25, "team_members": 5, "storage_mb": 5000},
    "pro": {"apps": 50, "api_calls_daily": 500000, "webhooks": 100, "team_members": 25, "storage_mb": 50000},
    "enterprise": {"apps": -1, "api_calls_daily": -1, "webhooks": -1, "team_members": -1, "storage_mb": -1},
}


def check_limits(plan: str, usage: dict) -> dict:
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    checks = []
    exceeded = False
    for resource, limit in limits.items():
        used = usage.get(resource, 0)
        if limit == -1:
            checks.append({"resource": resource, "used": used, "limit": "unlimited", "pct": 0, "ok": True})
        else:
            pct = round(used / max(limit, 1) * 100)
            ok = used <= limit
            if not ok:
                exceeded = True
            checks.append({"resource": resource, "used": used, "limit": limit, "pct": min(pct, 100), "ok": ok,
                            "warning": pct >= 80 and ok})
    return {"plan": plan, "checks": checks, "exceeded": exceeded,
            "upgrade_needed": exceeded, "next_plan": _next_plan(plan) if exceeded else None}


def _next_plan(current: str) -> str:
    order = ["free", "starter", "pro", "enterprise"]
    idx = order.index(current) if current in order else 0
    return order[min(idx + 1, len(order) - 1)]
