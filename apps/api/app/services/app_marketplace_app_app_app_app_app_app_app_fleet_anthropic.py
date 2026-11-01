"""Fleet Anthropic — track Claude API integration."""
from __future__ import annotations
def fleet_anthropic_status(projects: list[dict]) -> dict:
    active = [p for p in projects if p.get("active", True)]
    requests_24h = sum(p.get("requests_24h", 0) for p in projects)
    tokens_24h = sum(p.get("tokens_24h", 0) for p in projects)
    return {"projects": len(projects), "active": len(active), "requests_24h": requests_24h,
            "tokens_24h": tokens_24h, "all_active": len(active) == len(projects)}
