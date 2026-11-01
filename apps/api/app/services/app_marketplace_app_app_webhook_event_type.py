"""Webhook event type — event type registry with schema documentation."""

import html

EVENT_TYPES = {
    "app.installed": {"category": "Apps", "description": "An app was installed", "fields": ["app_id", "user_id", "timestamp"]},
    "app.uninstalled": {"category": "Apps", "description": "An app was uninstalled", "fields": ["app_id", "user_id"]},
    "app.updated": {"category": "Apps", "description": "App settings updated", "fields": ["app_id", "changes"]},
    "review.created": {"category": "Reviews", "description": "A new review was posted", "fields": ["review_id", "app_id", "rating"]},
    "deploy.started": {"category": "Deployments", "description": "Deployment started", "fields": ["deploy_id", "version", "environment"]},
    "deploy.completed": {"category": "Deployments", "description": "Deployment finished", "fields": ["deploy_id", "status", "duration_ms"]},
    "deploy.failed": {"category": "Deployments", "description": "Deployment failed", "fields": ["deploy_id", "error", "environment"]},
    "webhook.test": {"category": "System", "description": "Test webhook event", "fields": ["timestamp"]},
}


def list_event_types(*, category: str | None = None) -> dict:
    items = []
    for eid, info in EVENT_TYPES.items():
        if category and info["category"] != category:
            continue
        items.append({"id": eid, "description": info["description"],
                       "category": info["category"], "fields": info["fields"],
                       "field_count": len(info["fields"])})
    categories = sorted(set(e["category"] for e in EVENT_TYPES.values()))
    return {"events": items, "total": len(items), "categories": categories}


def get_event_schema(*, event_type: str) -> dict:
    info = EVENT_TYPES.get(event_type)
    if not info:
        return {"error": f"Unknown event: {event_type}"}
    return {"event_type": event_type, **info,
            "example": {f: f"<{f}>" for f in info["fields"]}}
