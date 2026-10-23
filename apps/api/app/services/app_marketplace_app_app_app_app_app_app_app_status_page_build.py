"""Status page builder — generate public status pages."""
from __future__ import annotations
import html


def build_status_page(title: str, components: list[dict], incidents: list[dict] | None = None) -> dict:
    safe_title = html.escape(title)
    statuses = {"operational": 0, "degraded": 0, "outage": 0, "maintenance": 0}
    items = []
    for c in components:
        st = c.get("status", "operational")
        statuses[st] = statuses.get(st, 0) + 1
        items.append({"name": html.escape(c["name"]), "status": st,
                       "uptime_pct": c.get("uptime_pct", 100.0)})
    all_ok = statuses["outage"] == 0 and statuses["degraded"] == 0
    overall = "operational" if all_ok else "degraded" if statuses["outage"] == 0 else "outage"
    return {"title": safe_title, "components": items, "overall": overall,
            "summary": statuses, "incident_count": len(incidents or []),
            "avg_uptime": round(sum(c["uptime_pct"] for c in items) / max(len(items), 1), 2)}
