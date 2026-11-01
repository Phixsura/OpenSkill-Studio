"""Cost estimator — predict infrastructure costs based on usage patterns."""


def estimate_monthly_cost(*, api_calls: int, storage_gb: float, bandwidth_gb: float,
                            sandbox_hours: float) -> dict:
    api_cost = max(0, (api_calls - 10000)) * 0.001  # $0.001 per call over free tier
    storage_cost = storage_gb * 0.25
    bandwidth_cost = bandwidth_gb * 0.10
    compute_cost = sandbox_hours * 0.05
    total = round(api_cost + storage_cost + bandwidth_cost + compute_cost, 2)
    return {
        "breakdown": {"api": round(api_cost, 2), "storage": round(storage_cost, 2),
                       "bandwidth": round(bandwidth_cost, 2), "compute": round(compute_cost, 2)},
        "total_usd": total, "free_tier_savings": round(min(api_calls, 10000) * 0.001, 2),
    }


def compare_plans_cost(*, usage: dict, plans: list[dict]) -> list[dict]:
    results = []
    for plan in plans:
        included = plan.get("included", {})
        overage = 0
        for key in ("api_calls", "storage_gb", "bandwidth_gb"):
            used = usage.get(key, 0)
            included_amount = included.get(key, 0)
            if used > included_amount:
                overage += (used - included_amount) * plan.get("overage_rates", {}).get(key, 0)
        total = plan.get("base_price", 0) + round(overage, 2)
        results.append({"plan": plan["name"], "base": plan.get("base_price", 0),
                         "overage": round(overage, 2), "total": total})
    return sorted(results, key=lambda r: r["total"])


def get_cost_optimization_tips(*, breakdown: dict) -> list[str]:
    tips = []
    if breakdown.get("api", 0) > 10:
        tips.append("Consider implementing response caching to reduce API calls")
    if breakdown.get("storage", 0) > 5:
        tips.append("Archive old data to reduce storage costs")
    if breakdown.get("bandwidth", 0) > 5:
        tips.append("Enable compression to reduce bandwidth usage")
    if breakdown.get("compute", 0) > 10:
        tips.append("Optimize sandbox execution time with lazy loading")
    return tips or ["Your costs are well optimized!"]
