"""Tests for App Webhook Event Router — subscriptions, routing, filters, dedup."""

import pytest

from app.services.app_webhook_event_router import (
    AppWebhookEventRouter,
    DeliveryPriority,
    EventSubscription,
    PlatformEvent,
    _compute_idempotency_key,
)


def _sub(app_id: str, event_type: str = "skill_pack.published",
         filters: dict | None = None,
         priority: DeliveryPriority = DeliveryPriority.NORMAL) -> EventSubscription:
    return EventSubscription(
        app_id=app_id, app_name=f"App {app_id}",
        event_type=event_type,
        webhook_url=f"https://{app_id}.example.com/hook",
        secret=f"secret-{app_id}",
        filters=filters, priority=priority,
    )


def _event(event_id: str = "evt-1", event_type: str = "skill_pack.published",
           org_id: str = "org-1", payload: dict | None = None) -> PlatformEvent:
    return PlatformEvent(
        event_id=event_id, event_type=event_type,
        payload=payload or {"pack_id": "pack-1", "name": "React Patterns"},
        org_id=org_id, user_id="user-1",
    )


class TestIdempotencyKey:
    def test_deterministic(self):
        k1 = _compute_idempotency_key("evt-1", "app-1")
        k2 = _compute_idempotency_key("evt-1", "app-1")
        assert k1 == k2

    def test_different_for_different_apps(self):
        k1 = _compute_idempotency_key("evt-1", "app-1")
        k2 = _compute_idempotency_key("evt-1", "app-2")
        assert k1 != k2

    def test_24_chars(self):
        assert len(_compute_idempotency_key("e", "a")) == 24


class TestSubscriptions:
    def test_subscribe(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        subs = router.get_subscriptions("skill_pack.published")
        assert len(subs) == 1
        assert subs[0].app_id == "app-1"

    def test_subscribe_update_in_place(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        updated = _sub("app-1")
        updated.webhook_url = "https://new-url.com/hook"
        router.subscribe(updated)
        subs = router.get_subscriptions("skill_pack.published")
        assert len(subs) == 1
        assert subs[0].webhook_url == "https://new-url.com/hook"

    def test_unsubscribe(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        removed = router.unsubscribe("app-1", "skill_pack.published")
        assert removed is True
        assert router.get_subscriptions("skill_pack.published") == []

    def test_unsubscribe_nonexistent(self):
        router = AppWebhookEventRouter()
        assert router.unsubscribe("app-x", "skill_pack.published") is False

    def test_unsubscribe_app_all(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", "skill_pack.published"))
        router.subscribe(_sub("app-1", "app.installed"))
        count = router.unsubscribe_app("app-1")
        assert count == 2

    def test_get_app_subscriptions(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", "skill_pack.published"))
        router.subscribe(_sub("app-1", "workflow.completed"))
        subs = router.get_app_subscriptions("app-1")
        assert len(subs) == 2
        types = [s.event_type for s in subs]
        assert "skill_pack.published" in types

    def test_inactive_excluded(self):
        router = AppWebhookEventRouter()
        sub = _sub("app-1")
        sub.active = False
        router.subscribe(sub)
        assert router.get_subscriptions("skill_pack.published") == []


class TestRouting:
    def test_route_to_subscriber(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        result = router.route(_event())
        assert result.matched == 1
        assert len(result.targets) == 1
        assert result.targets[0].app_id == "app-1"

    def test_route_to_multiple(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        router.subscribe(_sub("app-2"))
        result = router.route(_event())
        assert result.matched == 2

    def test_no_subscribers(self):
        router = AppWebhookEventRouter()
        result = router.route(_event())
        assert result.matched == 0
        assert result.targets == []

    def test_enriched_payload(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        result = router.route(_event())
        payload = result.targets[0].enriched_payload
        assert payload["event_id"] == "evt-1"
        assert payload["event_type"] == "skill_pack.published"
        assert payload["org_id"] == "org-1"
        assert payload["user_id"] == "user-1"
        assert "data" in payload

    def test_wildcard_subscription(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", "*"))  # wildcard
        result = router.route(_event(event_type="anything.happened"))
        assert result.matched == 1

    def test_priority_ordering(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("low", priority=DeliveryPriority.LOW))
        router.subscribe(_sub("high", priority=DeliveryPriority.HIGH))
        router.subscribe(_sub("normal", priority=DeliveryPriority.NORMAL))
        result = router.route(_event())
        app_ids = [t.app_id for t in result.targets]
        assert app_ids == ["high", "normal", "low"]


class TestFilters:
    def test_org_filter_matches(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", filters={"org_id": "org-1"}))
        result = router.route(_event(org_id="org-1"))
        assert result.matched == 1

    def test_org_filter_excludes(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", filters={"org_id": "org-2"}))
        result = router.route(_event(org_id="org-1"))
        assert result.matched == 0
        assert result.filtered_out == 1

    def test_payload_filter(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", filters={"name": "React Patterns"}))
        result = router.route(_event(payload={"name": "React Patterns"}))
        assert result.matched == 1

    def test_payload_filter_excludes(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", filters={"name": "Vue Basics"}))
        result = router.route(_event(payload={"name": "React Patterns"}))
        assert result.matched == 0

    def test_no_filter_matches_all(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1", filters=None))
        result = router.route(_event())
        assert result.matched == 1


class TestDedup:
    def test_same_event_deduped(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        r1 = router.route(_event(event_id="evt-1"))
        r2 = router.route(_event(event_id="evt-1"))
        assert r1.matched == 1
        assert r2.matched == 0
        assert r2.duplicates_skipped == 1

    def test_different_events_not_deduped(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        r1 = router.route(_event(event_id="evt-1"))
        r2 = router.route(_event(event_id="evt-2"))
        assert r1.matched == 1
        assert r2.matched == 1


class TestStats:
    def test_stats(self):
        router = AppWebhookEventRouter()
        router.subscribe(_sub("app-1"))
        router.subscribe(_sub("app-2", filters={"org_id": "org-99"}))
        router.route(_event())
        stats = router.stats
        assert stats["total_routed"] == 1
        assert stats["total_filtered"] == 1
        assert stats["subscription_count"] == 2
