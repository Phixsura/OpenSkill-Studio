"""Plan usage forecast — predict when plan limits will be reached."""

import math


def forecast_limit_breach(*, current_usage: float, limit: float,
                            daily_growth: float, days_history: int = 30) -> dict:
    if limit <= 0:
        return {"unlimited": True, "days_until_breach": -1}
    if current_usage >= limit:
        return {"breached": True, "days_until_breach": 0, "overage": round(current_usage - limit, 2)}
    if daily_growth <= 0:
        return {"breached": False, "days_until_breach": -1, "stable": True}
    remaining = limit - current_usage
    days = math.ceil(remaining / daily_growth)
    return {
        "breached": False,
        "current_usage": current_usage,
        "limit": limit,
        "daily_growth": round(daily_growth, 2),
        "days_until_breach": days,
        "projected_breach_usage": round(current_usage + daily_growth * days, 2),
        "urgency": "critical" if days <= 3 else "warning" if days <= 14 else "ok",
    }


def recommend_plan_upgrade(*, usage: dict, plans: list[dict]) -> dict:
    suitable = []
    for plan in plans:
        fits = all(usage.get(k, 0) <= plan["limits"].get(k, float("inf")) for k in usage)
        if fits:
            suitable.append(plan)
    suitable.sort(key=lambda p: p.get("price", 0))
    return {
        "current_fits": len(suitable) > 0,
        "recommended": suitable[0] if suitable else None,
        "all_suitable": suitable,
    }
