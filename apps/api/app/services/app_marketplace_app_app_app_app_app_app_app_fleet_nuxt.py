"""Fleet Nuxt — track Vue full-stack framework health."""
from __future__ import annotations
def fleet_nuxt_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    pages = sum(a.get("pages", 0) for a in apps)
    nitro_presets = len(set(a.get("preset", "node") for a in apps))
    return {"apps": len(apps), "deployed": len(deployed), "pages": pages,
            "presets": nitro_presets, "all_deployed": len(deployed) == len(apps)}
