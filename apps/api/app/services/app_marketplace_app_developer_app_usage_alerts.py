"""Usage alerts — automated alerts when usage approaches quota limits."""


def check_usage_thresholds(*, usage: dict, limits: dict, warning_pct: float = 80,
                              critical_pct: float = 95) -> list[dict]:
    alerts = []
    for resource, current in usage.items():
        limit = limits.get(resource, 0)
        if limit <= 0:
            continue
        pct = round(current / limit * 100, 1)
        if pct >= critical_pct:
            alerts.append({"resource": resource, "current": current, "limit": limit,
                           "usage_pct": pct, "level": "critical"})
        elif pct >= warning_pct:
            alerts.append({"resource": resource, "current": current, "limit": limit,
                           "usage_pct": pct, "level": "warning"})
    return alerts


def build_usage_forecast(*, current: int, daily_rate: float, limit: int) -> dict:
    if daily_rate <= 0:
        return {"days_until_limit": None, "will_exceed": False}
    remaining = limit - current
    days = round(remaining / daily_rate, 1)
    return {"days_until_limit": max(0, days), "will_exceed": days < 30,
            "projected_30d": round(current + daily_rate * 30)}


def recommend_plan_upgrade(*, alerts: list[dict], current_plan: str) -> dict | None:
    critical = [a for a in alerts if a["level"] == "critical"]
    if not critical:
        return None
    plans = {"free": "starter", "starter": "pro", "pro": "enterprise"}
    upgrade = plans.get(current_plan)
    if not upgrade:
        return None
    return {"current_plan": current_plan, "recommended": upgrade,
            "reason": f"{len(critical)} resources at critical usage",
            "resources": [a["resource"] for a in critical]}
