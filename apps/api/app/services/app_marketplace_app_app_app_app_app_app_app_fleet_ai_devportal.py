"""Fleet AI Developer Portal — track AI documentation and onboarding."""
from __future__ import annotations
def fleet_ai_devportal(portals: list[dict]) -> dict:
    active = [p for p in portals if p.get("active", True)]
    docs_pages = sum(p.get("docs_pages", 0) for p in portals)
    api_keys_issued = sum(p.get("api_keys", 0) for p in portals)
    developers = sum(p.get("developers", 0) for p in portals)
    return {"portals": len(portals), "active": len(active), "docs_pages": docs_pages,
            "api_keys": api_keys_issued, "developers": developers}
