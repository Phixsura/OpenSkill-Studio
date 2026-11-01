"""Deployment cadence analyzer — analyze deployment frequency and patterns."""
from __future__ import annotations
from collections import defaultdict


def analyze_cadence(deployments: list[dict], period_days: int = 30) -> dict:
    by_day: dict[str, int] = defaultdict(int)
    by_service: dict[str, int] = defaultdict(int)
    for d in deployments:
        day = d.get("date", "unknown")
        by_day[day] += 1
        by_service[d.get("service", "unknown")] += 1
    deploys_per_day = round(len(deployments) / max(period_days, 1), 2)
    peak_day = max(by_day.items(), key=lambda x: x[1]) if by_day else ("none", 0)
    return {"total_deploys": len(deployments), "deploys_per_day": deploys_per_day,
            "unique_days": len(by_day), "peak_day": peak_day[0], "peak_count": peak_day[1],
            "services_deployed": len(by_service), "period_days": period_days}


def cadence_health(deploys_per_day: float) -> dict:
    if deploys_per_day >= 1:
        level = "elite"
        label = "On-demand (multiple daily)"
    elif deploys_per_day >= 1/7:
        level = "high"
        label = "Weekly"
    elif deploys_per_day >= 1/30:
        level = "medium"
        label = "Monthly"
    else:
        level = "low"
        label = "Infrequent"
    return {"level": level, "label": label, "deploys_per_day": deploys_per_day}
