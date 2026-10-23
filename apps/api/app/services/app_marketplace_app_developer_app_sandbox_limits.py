"""Sandbox limits — enforce and monitor resource limits for sandboxed apps."""

PLAN_LIMITS = {
    "free": {"cpu_ms": 1000, "memory_mb": 64, "network_mb": 10, "storage_mb": 50, "max_duration_s": 30},
    "starter": {"cpu_ms": 5000, "memory_mb": 256, "network_mb": 100, "storage_mb": 500, "max_duration_s": 60},
    "pro": {"cpu_ms": 30000, "memory_mb": 1024, "network_mb": 1000, "storage_mb": 5000, "max_duration_s": 300},
}


def get_sandbox_limits(*, plan: str) -> dict:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["free"])


def check_sandbox_limits(*, usage: dict, plan: str) -> dict:
    limits = get_sandbox_limits(plan=plan)
    violations = []
    for resource, limit in limits.items():
        current = usage.get(resource, 0)
        if current > limit:
            violations.append({"resource": resource, "current": current, "limit": limit,
                               "overage_pct": round((current - limit) / limit * 100, 1)})
    return {"within_limits": len(violations) == 0, "violations": violations, "plan": plan}


def estimate_plan_for_usage(*, usage: dict) -> str:
    for plan in ["free", "starter", "pro"]:
        limits = PLAN_LIMITS[plan]
        if all(usage.get(r, 0) <= l for r, l in limits.items()):
            return plan
    return "enterprise"
