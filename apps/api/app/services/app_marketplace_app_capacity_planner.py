"""Capacity planner — predict resource needs based on growth trends."""

import math


def forecast_usage(*, current: int, growth_rate_pct: float, months: int) -> list[dict]:
    forecasts = []
    for m in range(1, months + 1):
        projected = math.ceil(current * (1 + growth_rate_pct / 100) ** m)
        forecasts.append({"month": m, "projected": projected})
    return forecasts


def recommend_plan(*, projected_api_calls: int, projected_storage_gb: float) -> dict:
    if projected_api_calls <= 10000 and projected_storage_gb <= 1:
        return {"plan": "free", "reason": "Usage within free tier limits"}
    if projected_api_calls <= 100000 and projected_storage_gb <= 10:
        return {"plan": "starter", "reason": "Moderate usage fits starter plan"}
    if projected_api_calls <= 1000000 and projected_storage_gb <= 100:
        return {"plan": "pro", "reason": "High usage needs pro features"}
    return {"plan": "enterprise", "reason": "Very high usage requires enterprise plan"}


def compute_scaling_trigger(*, current_load: float, max_capacity: float, threshold_pct: float = 80) -> dict:
    usage_pct = round(current_load / max(max_capacity, 1) * 100, 1)
    should_scale = usage_pct >= threshold_pct
    return {"usage_pct": usage_pct, "should_scale": should_scale,
            "recommended_capacity": math.ceil(max_capacity * 1.5) if should_scale else int(max_capacity)}
