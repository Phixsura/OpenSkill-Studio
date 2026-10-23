"""App integration card — third-party integration connection card."""

import html
from datetime import datetime, timezone

INTEGRATIONS = {
    "github": {"label": "GitHub", "icon": "🐙", "category": "SCM", "color": "#333"},
    "slack": {"label": "Slack", "icon": "💬", "category": "Communication", "color": "#4A154B"},
    "vercel": {"label": "Vercel", "icon": "▲", "category": "Deployment", "color": "#000"},
    "stripe": {"label": "Stripe", "icon": "💳", "category": "Payments", "color": "#635BFF"},
    "datadog": {"label": "Datadog", "icon": "🐶", "category": "Monitoring", "color": "#632CA6"},
    "sentry": {"label": "Sentry", "icon": "🔍", "category": "Error Tracking", "color": "#362D59"},
    "linear": {"label": "Linear", "icon": "📐", "category": "Project Management", "color": "#5E6AD2"},
    "notion": {"label": "Notion", "icon": "📝", "category": "Documentation", "color": "#000"},
}


def build_integration_card(*, integration_id: str, connected: bool = False,
                              last_sync: str | None = None) -> dict:
    info = INTEGRATIONS.get(integration_id)
    if not info:
        return {"error": f"Unknown integration: {integration_id}"}
    return {
        "id": integration_id, **info,
        "connected": connected,
        "last_sync": last_sync,
        "cta": "Disconnect" if connected else "Connect",
    }


def build_integrations_grid(*, connected: list[str]) -> dict:
    conn_set = set(connected)
    items = [build_integration_card(integration_id=iid, connected=iid in conn_set)
             for iid in INTEGRATIONS]
    connected_count = sum(1 for i in items if i.get("connected"))
    categories = sorted(set(i.get("category", "") for i in items if "category" in i))
    return {"integrations": items, "total": len(items),
            "connected": connected_count, "available": len(items) - connected_count,
            "categories": categories}
