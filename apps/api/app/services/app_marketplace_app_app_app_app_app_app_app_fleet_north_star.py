"""Fleet North Star metric — the single most important platform metric."""
from __future__ import annotations
def fleet_north_star(metrics: dict) -> dict:
    weekly_active = metrics.get("weekly_active_devs", 0)
    target = metrics.get("target", 1000)
    pct = round(weekly_active / max(target, 1) * 100, 1)
    return {"metric": "Weekly Active Developers", "current": weekly_active,
            "target": target, "achievement_pct": pct, "on_track": pct >= 80}
