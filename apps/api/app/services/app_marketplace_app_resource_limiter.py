"""Resource limiter — enforce compute resource limits for sandboxed apps."""


PLAN_RESOURCES = {
    "free": {"cpu_cores": 0.5, "memory_mb": 256, "storage_gb": 1, "bandwidth_gb": 5},
    "starter": {"cpu_cores": 1, "memory_mb": 512, "storage_gb": 5, "bandwidth_gb": 50},
    "pro": {"cpu_cores": 2, "memory_mb": 2048, "storage_gb": 20, "bandwidth_gb": 200},
    "enterprise": {"cpu_cores": 8, "memory_mb": 8192, "storage_gb": 100, "bandwidth_gb": -1},
}


def get_resource_limits(*, plan: str) -> dict:
    limits = PLAN_RESOURCES.get(plan)
    if not limits:
        return {"error": f"Unknown plan. Valid: {', '.join(sorted(PLAN_RESOURCES))}"}
    return {"plan": plan, "limits": limits,
            "unlimited_bandwidth": limits["bandwidth_gb"] == -1}


def check_resource_usage(*, plan: str, usage: dict) -> dict:
    limits = PLAN_RESOURCES.get(plan, PLAN_RESOURCES["free"])
    violations = []
    for resource, limit in limits.items():
        if limit == -1:
            continue
        current = usage.get(resource, 0)
        if current > limit:
            violations.append({
                "resource": resource, "limit": limit, "current": current,
                "overage_pct": round((current - limit) / limit * 100, 1),
            })
    return {
        "plan": plan,
        "violations": violations,
        "violation_count": len(violations),
        "within_limits": len(violations) == 0,
    }
