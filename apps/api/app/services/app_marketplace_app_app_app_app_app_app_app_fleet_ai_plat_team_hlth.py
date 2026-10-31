"""Fleet AI Platform Team Health — track engineering team health metrics."""
from __future__ import annotations
def fleet_ai_platform_team_health(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    teams = sum(t.get("teams", 0) for t in trackers)
    happiness = round(sum(t.get("happiness", 0) for t in trackers) / max(len(trackers), 1), 1)
    burnout_risk = round(sum(t.get("burnout_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "teams": teams,
            "happiness": happiness, "burnout_risk": burnout_risk, "healthy": happiness > 80 and burnout_risk < 15}
