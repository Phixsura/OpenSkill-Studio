"""Fleet team velocity — track engineering team productivity."""
from __future__ import annotations
def fleet_team_velocity(teams: list[dict]) -> dict:
    total_points = sum(t.get("story_points", 0) for t in teams)
    avg_vel = round(total_points / max(len(teams), 1), 1)
    top = max(teams, key=lambda t: t.get("story_points", 0)) if teams else None
    return {"teams": len(teams), "total_points": total_points, "avg_velocity": avg_vel,
            "top_team": top.get("name") if top else None}
