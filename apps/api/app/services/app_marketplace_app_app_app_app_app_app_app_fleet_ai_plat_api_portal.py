"""Fleet AI API Portal v2 — track developer API portal and documentation."""
from __future__ import annotations
def fleet_ai_api_portal_v2(portals: list[dict]) -> dict:
    active = [p for p in portals if p.get("active", True)]
    apis = sum(p.get("apis", 0) for p in portals)
    docs_pages = sum(p.get("pages", 0) for p in portals)
    developers = sum(p.get("developers", 0) for p in portals)
    api_keys = sum(p.get("api_keys", 0) for p in portals)
    return {"portals": len(portals), "active": len(active), "apis": apis,
            "pages": docs_pages, "developers": developers, "api_keys": api_keys, "adopted": developers > 1000}
