from app.services.app_marketplace_webhook_events import (
    WebhookEventBuilder, EventCategory, WEBHOOK_EVENT_TYPES,
)


def test_build_valid_event():
    event, msg = WebhookEventBuilder.build(
        "extension.published", "ext-1",
        {"version": "2.0.0", "changelog": "New features"},
        actor_id="dev-1",
    )
    assert event is not None
    assert event.event_type == "extension.published"
    assert event.payload["version"] == "2.0.0"


def test_build_invalid_type():
    event, msg = WebhookEventBuilder.build("nonexistent.event", "ext-1", {})
    assert event is None
    assert "Unknown" in msg


def test_list_all_events():
    events = WebhookEventBuilder.list_event_types()
    assert len(events) == len(WEBHOOK_EVENT_TYPES)


def test_list_by_category():
    billing = WebhookEventBuilder.list_event_types(EventCategory.BILLING)
    assert len(billing) == 3
    assert all(e["category"] == "billing" for e in billing)


def test_serialize():
    event, _ = WebhookEventBuilder.build(
        "install.created", "ext-2", {"org_id": "org-1"}, org_id="org-1",
    )
    serialized = WebhookEventBuilder.serialize(event)
    assert serialized["type"] == "install.created"
    assert "id" in serialized
    assert "timestamp" in serialized
    assert serialized["data"]["org_id"] == "org-1"


def test_event_categories():
    security = WebhookEventBuilder.list_event_types(EventCategory.SECURITY)
    assert any("vulnerability" in e["name"] for e in security)
    install = WebhookEventBuilder.list_event_types(EventCategory.INSTALL)
    assert len(install) == 2
