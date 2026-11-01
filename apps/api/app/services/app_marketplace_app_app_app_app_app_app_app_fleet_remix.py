"""Fleet Remix — track full-stack React framework health."""
from __future__ import annotations
def fleet_remix_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    total_loaders = sum(a.get("loaders", 0) for a in apps)
    total_actions = sum(a.get("actions", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "loaders": total_loaders,
            "actions": total_actions, "all_deployed": len(deployed) == len(apps)}
