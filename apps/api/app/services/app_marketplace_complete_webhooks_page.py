"""Complete webhooks page — all webhook management in one view."""


def build_complete_webhooks_page(*, app: dict, endpoints: list[dict], deliveries: list[dict],
                                     event_types: list[str], retry_policy: dict) -> dict:
    active = sum(1 for e in endpoints if e.get("active"))
    success = sum(1 for d in deliveries if d.get("success"))
    total_deliveries = len(deliveries)
    return {
        "page_type": "webhooks_management",
        "app": {"id": app["id"], "name": app["name"]},
        "overview": {"total_endpoints": len(endpoints), "active": active,
                      "delivery_rate": round(success / max(total_deliveries, 1) * 100, 1),
                      "total_deliveries": total_deliveries},
        "tabs": [
            {"key": "endpoints", "title": f"Endpoints ({len(endpoints)})", "icon": "🔗"},
            {"key": "deliveries", "title": "Recent Deliveries", "icon": "📬"},
            {"key": "events", "title": f"Events ({len(event_types)})", "icon": "📋"},
            {"key": "retry", "title": "Retry Policy", "icon": "🔄"},
            {"key": "debugger", "title": "Debugger", "icon": "🔍"},
        ],
        "retry_policy": retry_policy,
        "available_events": event_types,
    }
