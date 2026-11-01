"""Notification dispatcher — fan out notifications to multiple channels."""

from datetime import datetime, timezone


def dispatch_notification(*, channels: list[str], title: str, message: str,
                            severity: str = "info", data: dict | None = None) -> dict:
    results = []
    for ch in channels:
        results.append({"channel": ch, "status": "sent", "title": title})
    return {"dispatched": len(results), "channels": results, "severity": severity,
            "timestamp": datetime.now(timezone.utc).isoformat()}


def build_notification_payload(*, event_type: str, app: dict, details: dict) -> dict:
    templates = {
        "install": {"title": f"New install: {app.get('name')}", "icon": "📥"},
        "review": {"title": f"New review on {app.get('name')}", "icon": "⭐"},
        "error": {"title": f"Error in {app.get('name')}", "icon": "❌"},
        "deploy": {"title": f"Deployed {app.get('name')}", "icon": "🚀"},
    }
    tmpl = templates.get(event_type, {"title": event_type, "icon": "📌"})
    return {**tmpl, "details": details, "app_id": app.get("id"), "event_type": event_type}


def get_dispatch_stats(*, dispatches: list[dict]) -> dict:
    total = sum(d.get("dispatched", 0) for d in dispatches)
    by_severity = {}
    for d in dispatches:
        s = d.get("severity", "info")
        by_severity[s] = by_severity.get(s, 0) + 1
    return {"total_dispatched": total, "dispatch_count": len(dispatches), "by_severity": by_severity}
