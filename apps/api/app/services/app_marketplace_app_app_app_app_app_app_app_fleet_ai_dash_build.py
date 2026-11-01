"""Fleet AI Dashboard Builder — track AI observability dashboard creation."""
from __future__ import annotations
def fleet_ai_dashboard_builder(builders: list[dict]) -> dict:
    active = [b for b in builders if b.get("active", True)]
    dashboards = sum(b.get("dashboards", 0) for b in builders)
    panels = sum(b.get("panels", 0) for b in builders)
    viewers_24h = sum(b.get("viewers_24h", 0) for b in builders)
    return {"builders": len(builders), "active": len(active), "dashboards": dashboards,
            "panels": panels, "viewers_24h": viewers_24h, "popular": viewers_24h > 100}
