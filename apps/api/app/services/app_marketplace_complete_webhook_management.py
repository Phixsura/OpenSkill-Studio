"""Complete webhook management — master aggregator for webhook configuration and monitoring."""


def build_complete_webhook_management(*, webhooks: list[dict], delivery_stats: dict,
                                         recent_attempts: list[dict], event_types: list[str]) -> dict:
    active = sum(1 for w in webhooks if w.get("active"))
    return {
        "page_type": "webhook_management",
        "overview": {"total": len(webhooks), "active": active, "inactive": len(webhooks) - active},
        "delivery_stats": delivery_stats,
        "sections": [
            {"key": "endpoints", "title": f"Endpoints ({len(webhooks)})", "icon": "🔗", "data": webhooks},
            {"key": "deliveries", "title": "Recent Deliveries", "icon": "📬", "data": recent_attempts[:20]},
            {"key": "events", "title": f"Event Types ({len(event_types)})", "icon": "📋", "data": event_types},
            {"key": "debugger", "title": "Debugger", "icon": "🔍"},
        ],
    }
