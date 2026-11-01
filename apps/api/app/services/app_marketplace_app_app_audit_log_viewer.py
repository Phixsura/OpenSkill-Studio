"""Audit log viewer — security event log with filtering."""

import html
from datetime import datetime, timezone

SEVERITY_ICONS = {"info": "ℹ️", "warning": "⚠️", "critical": "🚨"}


def build_audit_log(*, events: list[dict], filter_severity: str | None = None) -> dict:
    items = []
    for e in events:
        sev = e.get("severity", "info")
        if filter_severity and sev != filter_severity:
            continue
        items.append({
            "id": e.get("id", ""),
            "action": html.escape(e.get("action", "")),
            "actor": html.escape(e.get("actor", "system")),
            "target": html.escape(e.get("target", "")),
            "severity": sev,
            "icon": SEVERITY_ICONS.get(sev, "📝"),
            "ip": e.get("ip", ""),
            "timestamp": e.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    by_severity = {}
    for i in items:
        by_severity[i["severity"]] = by_severity.get(i["severity"], 0) + 1
    return {"events": items, "total": len(items), "by_severity": by_severity}
