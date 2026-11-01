"""Tests for Consumer Webhook Event Bus service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_event_bus import (
    EventBus, Subscription, Event,
)


class TestEventBus:
    def test_subscribe_and_publish(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "order.created", "https://hook.com/a"))
        result = svc.publish(Event("e1", "order.created", {"id": 1}))
        assert result["delivered_to"] == 1

    def test_topic_mismatch(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "order.created", "https://hook.com/a"))
        result = svc.publish(Event("e1", "user.created", {"id": 1}))
        assert result["delivered_to"] == 0

    def test_wildcard_topic(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "order.*", "https://hook.com/a"))
        r1 = svc.publish(Event("e1", "order.created", {}))
        r2 = svc.publish(Event("e2", "order.updated", {}))
        r3 = svc.publish(Event("e3", "user.created", {}))
        assert r1["delivered_to"] == 1
        assert r2["delivered_to"] == 1
        assert r3["delivered_to"] == 0

    def test_global_wildcard(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "*", "https://hook.com/all"))
        result = svc.publish(Event("e1", "anything.here", {}))
        assert result["delivered_to"] == 1

    def test_unsubscribe(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "test", "https://hook.com"))
        svc.unsubscribe("s1")
        result = svc.publish(Event("e1", "test", {}))
        assert result["delivered_to"] == 0

    def test_toggle(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "test", "https://hook.com"))
        svc.toggle("s1", False)
        r = svc.publish(Event("e1", "test", {}))
        assert r["delivered_to"] == 0
        svc.toggle("s1", True)
        r = svc.publish(Event("e2", "test", {}))
        assert r["delivered_to"] == 1

    def test_get_subscribers(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "order.*", "https://a.com"))
        svc.subscribe(Subscription("s2", "c2", "user.*", "https://b.com"))
        subs = svc.get_subscribers("order.created")
        assert len(subs) == 1

    def test_delivered_count(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "test", "https://hook.com"))
        svc.publish(Event("e1", "test", {}))
        svc.publish(Event("e2", "test", {}))
        subs = svc.list_subscriptions()
        assert subs[0]["delivered"] == 2

    def test_stats(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "a", "https://a.com"))
        svc.publish(Event("e1", "a", {}))
        svc.publish(Event("e2", "b", {}))
        stats = svc.get_stats()
        assert stats["total_events"] == 2
        assert stats["unique_topics"] == 2

    def test_duplicate_sub(self):
        svc = EventBus()
        svc.subscribe(Subscription("s1", "c1", "test", "https://a.com"))
        with pytest.raises(ValueError):
            svc.subscribe(Subscription("s1", "c2", "test", "https://b.com"))

    def test_isolation(self):
        a, b = EventBus(), EventBus()
        a.subscribe(Subscription("s1", "c1", "test", "https://a.com"))
        assert b.publish(Event("e1", "test", {}))["delivered_to"] == 0
