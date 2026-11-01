"""Fleet Amplify — track AWS full-stack platform."""
from __future__ import annotations
def fleet_amplify_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    backends = sum(a.get("backends", 0) for a in apps)
    branches = sum(a.get("branches", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "backends": backends,
            "branches": branches, "all_deployed": len(deployed) == len(apps)}
