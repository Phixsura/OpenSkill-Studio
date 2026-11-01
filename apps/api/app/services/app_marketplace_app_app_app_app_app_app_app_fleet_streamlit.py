"""Fleet Streamlit — track data app framework."""
from __future__ import annotations
def fleet_streamlit_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    viewers_24h = sum(a.get("viewers_24h", 0) for a in apps)
    components = sum(a.get("components", 0) for a in apps)
    return {"apps": len(apps), "deployed": len(deployed), "viewers_24h": viewers_24h,
            "components": components, "all_deployed": len(deployed) == len(apps)}
