"""Usage limits — enforce per-plan resource quotas."""


def check_usage_limit(*, current: int, limit: int, resource: str) -> dict:
    remaining = max(0, limit - current)
    pct = round(current / max(limit, 1) * 100, 1)
    exceeded = current >= limit
    return {
        "resource": resource, "current": current, "limit": limit,
        "remaining": remaining, "usage_pct": pct, "exceeded": exceeded,
        "warning": pct >= 80 and not exceeded,
    }


def get_plan_limits(*, plan: str) -> dict:
    plans = {
        "free": {"api_calls": 1000, "webhooks": 3, "secrets": 5, "team_members": 1},
        "starter": {"api_calls": 10000, "webhooks": 10, "secrets": 20, "team_members": 3},
        "pro": {"api_calls": 100000, "webhooks": 50, "secrets": 100, "team_members": 10},
        "enterprise": {"api_calls": 1000000, "webhooks": 500, "secrets": 500, "team_members": 100},
    }
    return plans.get(plan, plans["free"])


def check_all_limits(*, usage: dict, plan: str) -> dict:
    limits = get_plan_limits(plan=plan)
    results = {}
    any_exceeded = False
    for resource, limit in limits.items():
        current = usage.get(resource, 0)
        check = check_usage_limit(current=current, limit=limit, resource=resource)
        results[resource] = check
        if check["exceeded"]:
            any_exceeded = True
    return {"limits": results, "any_exceeded": any_exceeded, "plan": plan}
