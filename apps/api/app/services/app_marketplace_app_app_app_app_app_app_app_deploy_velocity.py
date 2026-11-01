"""Deployment velocity tracker — measure how fast teams ship."""
from __future__ import annotations


def calculate_velocity(deploys: list[dict], period_days: int = 30) -> dict:
    total = len(deploys)
    per_day = round(total / max(period_days, 1), 1)
    by_team: dict[str, int] = {}
    by_env: dict[str, int] = {}
    success = 0
    for d in deploys:
        team = d.get("team", "unknown")
        env = d.get("environment", "production")
        by_team[team] = by_team.get(team, 0) + 1
        by_env[env] = by_env.get(env, 0) + 1
        if d.get("status") == "success":
            success += 1
    fastest_team = max(by_team, key=by_team.get) if by_team else None
    return {"total": total, "per_day": per_day, "by_team": by_team,
            "by_environment": by_env, "success_rate": round(success / max(total, 1) * 100),
            "fastest_team": fastest_team, "period_days": period_days}
