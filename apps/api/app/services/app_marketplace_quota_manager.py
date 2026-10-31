"""Quota manager — manage and enforce resource quotas across apps."""

PLAN_QUOTAS = {
    "free": {"apps": 1, "api_calls_per_day": 1000, "webhooks": 3, "team_members": 1, "storage_mb": 50},
    "starter": {"apps": 5, "api_calls_per_day": 50000, "webhooks": 10, "team_members": 5, "storage_mb": 500},
    "pro": {"apps": 25, "api_calls_per_day": 500000, "webhooks": 50, "team_members": 20, "storage_mb": 5000},
    "enterprise": {"apps": -1, "api_calls_per_day": -1, "webhooks": -1, "team_members": -1, "storage_mb": -1},
}


def get_quotas(*, plan: str) -> dict:
    return PLAN_QUOTAS.get(plan, PLAN_QUOTAS["free"])


def check_quota(*, plan: str, resource: str, current: int) -> dict:
    quotas = get_quotas(plan=plan)
    limit = quotas.get(resource, 0)
    if limit == -1:
        return {"allowed": True, "unlimited": True, "remaining": -1}
    remaining = max(0, limit - current)
    return {"allowed": current < limit, "unlimited": False, "current": current,
            "limit": limit, "remaining": remaining,
            "usage_pct": round(current / max(limit, 1) * 100, 1)}


def compare_plan_quotas(*, current_plan: str, target_plan: str) -> dict:
    current = get_quotas(plan=current_plan)
    target = get_quotas(plan=target_plan)
    comparison = {}
    for resource in current:
        cur = current[resource]
        tgt = target[resource]
        comparison[resource] = {"current": cur, "target": tgt,
                                 "upgrade": "unlimited" if tgt == -1 else f"{tgt - cur:+d}" if cur != -1 else "n/a"}
    return {"current_plan": current_plan, "target_plan": target_plan, "comparison": comparison}
