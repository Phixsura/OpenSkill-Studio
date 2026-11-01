"""Fleet Developer Portal v9 — track dev portal usage and engagement."""
from __future__ import annotations
def fleet_developer_portal_v9(portals: list[dict]) -> dict:
    active_devs = sum(p.get("active_developers", 0) for p in portals)
    api_keys_issued = sum(p.get("api_keys_issued", 0) for p in portals)
    docs_views = sum(p.get("docs_views_today", 0) for p in portals)
    return {"portals": len(portals), "active_developers": active_devs, "api_keys_issued": api_keys_issued,
            "docs_views_today": docs_views, "healthy": active_devs > 0}
