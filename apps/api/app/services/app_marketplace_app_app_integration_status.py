"""Integration status — third-party service connection status."""

import html

INTEGRATIONS = {
    "github": {"label": "GitHub", "icon": "🐙", "category": "SCM"},
    "slack": {"label": "Slack", "icon": "💬", "category": "Communication"},
    "vercel": {"label": "Vercel", "icon": "▲", "category": "Deployment"},
    "stripe": {"label": "Stripe", "icon": "💳", "category": "Payments"},
    "datadog": {"label": "Datadog", "icon": "🐶", "category": "Monitoring"},
    "sentry": {"label": "Sentry", "icon": "🔍", "category": "Error Tracking"},
}


def get_integration_status(*, connected: list[str]) -> dict:
    conn_set = set(connected)
    items = []
    for iid, info in INTEGRATIONS.items():
        items.append({**info, "id": iid, "connected": iid in conn_set})
    connected_count = sum(1 for i in items if i["connected"])
    return {"integrations": items, "total": len(items),
            "connected": connected_count, "available": len(items) - connected_count}
