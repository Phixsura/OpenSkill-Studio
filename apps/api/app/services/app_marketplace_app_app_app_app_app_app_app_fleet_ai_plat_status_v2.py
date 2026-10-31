"""Fleet AI Status Page v2 — track public platform status communication."""
from __future__ import annotations
def fleet_ai_status_page_v2(pages: list[dict]) -> dict:
    active = [p for p in pages if p.get("active", True)]
    components = sum(p.get("components", 0) for p in pages)
    operational = sum(p.get("operational", 0) for p in pages)
    incidents_30d = sum(p.get("incidents", 0) for p in pages)
    uptime = round(sum(p.get("uptime_pct", 0) for p in pages) / max(len(pages), 1), 3)
    return {"pages": len(pages), "active": len(active), "components": components,
            "operational": operational, "incidents_30d": incidents_30d, "uptime": uptime,
            "status": "🟢 ALL OPERATIONAL" if operational == components else "🟡 DEGRADED"}
