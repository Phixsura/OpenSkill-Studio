"""Fleet Contentful — track headless CMS API."""
from __future__ import annotations
def fleet_contentful_status(spaces: list[dict]) -> dict:
    active = [s for s in spaces if s.get("active", True)]
    entries = sum(s.get("entries", 0) for s in spaces)
    api_calls = sum(s.get("api_calls_24h", 0) for s in spaces)
    return {"spaces": len(spaces), "active": len(active), "entries": entries,
            "api_calls_24h": api_calls, "all_active": len(active) == len(spaces)}
