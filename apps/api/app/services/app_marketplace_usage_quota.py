"""Usage quota — track and enforce API usage limits per plan."""


PLAN_LIMITS = {
    "free": {"api_calls": 1000, "storage_mb": 100, "webhooks": 3, "team_members": 1},
    "starter": {"api_calls": 10000, "storage_mb": 1024, "webhooks": 10, "team_members": 5},
    "pro": {"api_calls": 100000, "storage_mb": 10240, "webhooks": 50, "team_members": 25},
    "enterprise": {"api_calls": -1, "storage_mb": -1, "webhooks": -1, "team_members": -1},  # unlimited
}


def get_usage_summary(*, plan: str, usage: dict) -> dict:
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    resources = []
    for key, limit in limits.items():
        current = usage.get(key, 0)
        is_unlimited = limit == -1
        pct = 0 if is_unlimited else round(current / limit * 100, 1) if limit > 0 else 100
        resources.append({
            "resource": key, "current": current, "limit": limit,
            "unlimited": is_unlimited, "usage_pct": pct,
            "warning": not is_unlimited and pct >= 80,
            "exceeded": not is_unlimited and pct >= 100,
        })
    return {"plan": plan, "resources": resources,
            "any_exceeded": any(r["exceeded"] for r in resources),
            "any_warning": any(r["warning"] for r in resources)}


def check_quota(*, plan: str, resource: str, current: int) -> dict:
    limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])
    limit = limits.get(resource, 0)
    if limit == -1:
        return {"allowed": True, "remaining": -1, "unlimited": True}
    remaining = max(limit - current, 0)
    return {"allowed": current < limit, "remaining": remaining, "unlimited": False,
            "upgrade_needed": current >= limit}
