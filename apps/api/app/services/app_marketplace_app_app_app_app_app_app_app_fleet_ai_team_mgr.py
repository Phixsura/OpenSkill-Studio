"""Fleet AI Team Manager — track AI team collaboration and permissions."""
from __future__ import annotations
def fleet_ai_team_manager(managers: list[dict]) -> dict:
    active = [m for m in managers if m.get("active", True)]
    teams = sum(m.get("teams", 0) for m in managers)
    members = sum(m.get("members", 0) for m in managers)
    projects = sum(m.get("projects", 0) for m in managers)
    return {"managers": len(managers), "active": len(active), "teams": teams,
            "members": members, "projects": projects, "organized": teams > 0}
