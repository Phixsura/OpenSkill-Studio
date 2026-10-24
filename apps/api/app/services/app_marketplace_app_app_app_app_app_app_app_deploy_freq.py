"""Deployment frequency tracker — DORA metric: how often do we deploy?"""
from __future__ import annotations
from collections import defaultdict


def calculate_frequency(deployments: list[dict], period_days: int = 30) -> dict:
    if not deployments:
        return {"frequency": "none", "deploys_per_day": 0, "total": 0}
    total = len(deployments)
    per_day = round(total / max(period_days, 1), 2)
    by_env: dict[str, int] = defaultdict(int)
    for d in deployments:
        by_env[d.get("env", "unknown")] += 1
    if per_day >= 1:
        freq = "on_demand"
    elif per_day >= 1/7:
        freq = "weekly"
    elif per_day >= 1/30:
        freq = "monthly"
    else:
        freq = "rare"
    return {"frequency": freq, "deploys_per_day": per_day,
            "total": total, "period_days": period_days,
            "by_env": dict(by_env)}


def lead_time(commits: list[dict]) -> dict:
    if not commits:
        return {"avg_hours": 0, "total": 0}
    times = [c.get("lead_time_hours", 0) for c in commits]
    return {"avg_hours": round(sum(times) / len(times), 1),
            "min_hours": min(times), "max_hours": max(times),
            "total": len(commits)}
