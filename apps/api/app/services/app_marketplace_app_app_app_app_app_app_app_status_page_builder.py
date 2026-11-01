"""Status page builder — public status page with components and incidents."""
from __future__ import annotations
import html


def build_status_page(*, title: str, components: list[dict],
                        incidents: list[dict] | None = None) -> dict:
    safe_title = html.escape(title)
    comp_results = []
    all_operational = True
    for c in components:
        status = c.get("status", "operational")
        if status != "operational":
            all_operational = False
        comp_results.append({
            "name": html.escape(c["name"]), "status": status,
            "description": html.escape(c.get("description", "")),
            "uptime_pct": c.get("uptime_pct", 100),
        })
    active_incidents = [
        {"title": html.escape(i.get("title", "")),
         "status": i.get("status", "investigating"),
         "impact": i.get("impact", "none"),
         "updated": i.get("updated", "")}
        for i in (incidents or []) if i.get("status") != "resolved"
    ]
    overall = "operational" if all_operational and not active_incidents else \
              "degraded" if any(c["status"] == "degraded" for c in comp_results) else \
              "major_outage" if any(c["status"] == "major_outage" for c in comp_results) else "partial_outage"
    return {
        "title": safe_title, "overall": overall,
        "components": comp_results, "component_count": len(comp_results),
        "active_incidents": active_incidents,
        "incident_count": len(active_incidents),
        "all_operational": all_operational and not active_incidents,
    }
