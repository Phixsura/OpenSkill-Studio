"""Fleet SvelteKit — track Svelte full-stack framework."""
from __future__ import annotations
def fleet_sveltekit_status(apps: list[dict]) -> dict:
    deployed = [a for a in apps if a.get("deployed", True)]
    routes = sum(a.get("routes", 0) for a in apps)
    ssr_pct = round(sum(a.get("ssr_pct", 0) for a in apps) / max(len(apps), 1), 1)
    return {"apps": len(apps), "deployed": len(deployed), "routes": routes,
            "ssr_pct": ssr_pct, "all_deployed": len(deployed) == len(apps)}
