"""Fleet Astro — track content-focused web framework."""
from __future__ import annotations
def fleet_astro_status(sites: list[dict]) -> dict:
    deployed = [s for s in sites if s.get("deployed", True)]
    total_pages = sum(s.get("pages", 0) for s in sites)
    islands = sum(s.get("islands", 0) for s in sites)
    return {"sites": len(sites), "deployed": len(deployed), "pages": total_pages,
            "islands": islands, "all_deployed": len(deployed) == len(sites)}
