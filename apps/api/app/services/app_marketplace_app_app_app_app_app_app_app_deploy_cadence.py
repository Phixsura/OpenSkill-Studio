"""Deployment cadence tracker — measure deployment frequency and patterns."""
from __future__ import annotations


def track_cadence(deploys: list[dict], period_days: int = 30) -> dict:
    total = len(deploys)
    per_day = round(total / max(period_days, 1), 1)
    per_week = round(per_day * 7, 1)
    by_day: dict[str, int] = {}
    by_env: dict[str, int] = {}
    for d in deploys:
        day = d.get("day_of_week", "unknown")
        env = d.get("environment", "production")
        by_day[day] = by_day.get(day, 0) + 1
        by_env[env] = by_env.get(env, 0) + 1
    busiest_day = max(by_day, key=by_day.get) if by_day else None
    # DORA classification
    dora_level = "elite" if per_day >= 1 else "high" if per_week >= 1 else "medium" if total >= 4 else "low"
    return {"total": total, "per_day": per_day, "per_week": per_week,
            "by_day": by_day, "by_environment": by_env,
            "busiest_day": busiest_day, "dora_level": dora_level,
            "period_days": period_days}
