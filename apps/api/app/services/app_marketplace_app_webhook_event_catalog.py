"""Webhook event catalog — browsable catalog of available webhook events."""


EVENT_CATALOG = {
    "app": {
        "label": "App Events",
        "events": {
            "app.installed": {"description": "App installed by a user", "payload_example": {"app_id": "a1", "user_id": "u1"}},
            "app.uninstalled": {"description": "App uninstalled", "payload_example": {"app_id": "a1", "user_id": "u1"}},
            "app.updated": {"description": "App version updated", "payload_example": {"app_id": "a1", "version": "2.0"}},
            "app.published": {"description": "New app published to marketplace", "payload_example": {"app_id": "a1"}},
        },
    },
    "review": {
        "label": "Review Events",
        "events": {
            "review.created": {"description": "New review submitted", "payload_example": {"review_id": "r1", "rating": 5}},
            "review.updated": {"description": "Review edited", "payload_example": {"review_id": "r1"}},
        },
    },
    "billing": {
        "label": "Billing Events",
        "events": {
            "payment.completed": {"description": "Payment processed", "payload_example": {"amount": 9.99, "currency": "USD"}},
            "subscription.created": {"description": "New subscription", "payload_example": {"plan": "pro"}},
            "subscription.cancelled": {"description": "Subscription cancelled", "payload_example": {"plan": "pro"}},
        },
    },
}


def list_event_catalog(*, category: str | None = None) -> dict:
    if category and category not in EVENT_CATALOG:
        return {"error": f"Unknown category. Valid: {', '.join(sorted(EVENT_CATALOG))}"}
    cats = {category: EVENT_CATALOG[category]} if category else EVENT_CATALOG
    result = []
    for cat_id, cat_info in cats.items():
        events = [{"event": eid, **einfo} for eid, einfo in cat_info["events"].items()]
        result.append({"category": cat_id, "label": cat_info["label"], "events": events})
    total_events = sum(len(c["events"]) for c in result)
    return {"categories": result, "total_events": total_events}


def get_event_detail(*, event_name: str) -> dict:
    for cat_info in EVENT_CATALOG.values():
        if event_name in cat_info["events"]:
            return {"event": event_name, **cat_info["events"][event_name], "found": True}
    return {"event": event_name, "found": False, "error": "Event not found"}
