"""Fleet Pages — track JAMstack deployment platform."""
from __future__ import annotations
def fleet_pages_status(projects: list[dict]) -> dict:
    deployed = [p for p in projects if p.get("deployed", True)]
    builds_24h = sum(p.get("builds_24h", 0) for p in projects)
    domains = sum(p.get("custom_domains", 0) for p in projects)
    return {"projects": len(projects), "deployed": len(deployed), "builds_24h": builds_24h,
            "custom_domains": domains, "all_deployed": len(deployed) == len(projects)}
