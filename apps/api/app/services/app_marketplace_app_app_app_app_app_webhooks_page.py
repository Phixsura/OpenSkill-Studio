"""App webhooks page — complete webhook management for an app."""

import html


def build_webhooks_page(*, app_name: str, webhooks: list[dict],
                           recent_deliveries: list[dict]) -> dict:
    items = []
    for wh in webhooks:
        items.append({
            "id": wh.get("id", ""),
            "url": html.escape(wh.get("url", "")),
            "events": wh.get("events", []),
            "active": wh.get("active", True),
            "success_rate": wh.get("success_rate", 100),
        })
    active = sum(1 for w in items if w["active"])
    total_deliveries = len(recent_deliveries)
    success = sum(1 for d in recent_deliveries if d.get("success"))
    overall_rate = round(success / max(total_deliveries, 1) * 100, 1)
    return {
        "app_name": html.escape(app_name),
        "webhooks": items, "total_webhooks": len(items), "active": active,
        "delivery_stats": {
            "total": total_deliveries, "success": success,
            "failed": total_deliveries - success,
            "success_rate": overall_rate,
        },
        "health": "good" if overall_rate >= 95 else "warning" if overall_rate >= 80 else "critical",
    }
