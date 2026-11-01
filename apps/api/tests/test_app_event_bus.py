"""Tests for App Event Bus — subscribe, publish, wildcard, history."""

import pytest

from app.services.app_event_bus import AppEventBus, Event


def _event(event_id="e1", event_type="user.created", installation_id="inst-1"):
    return Event(event_id=event_id, event_type=event_type,
                 payload={"user": "alice"}, installation_id=installation_id)


class TestSubscribe:
    def test_subscribe(self):
        bus = AppEventBus()
        sub = bus.subscribe("inst-1", "sub-1", event_types=["user.created"])
        assert sub.subscription_id == "sub-1"
        assert sub.event_types == ["user.created"]

    def test_wildcard_subscribe(self):
        bus = AppEventBus()
        sub = bus.subscribe("inst-1", "sub-1")
        assert sub.event_types is None

    def test_duplicate(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1")
        with pytest.raises(ValueError, match="already exists"):
            bus.subscribe("inst-1", "sub-1")

    def test_missing_id(self):
        bus = AppEventBus()
        with pytest.raises(ValueError):
            bus.subscribe("inst-1", "")


class TestPublish:
    def test_publish_to_matching(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1", event_types=["user.created"])
        delivered = bus.publish(_event())
        assert len(delivered) == 1
        assert delivered[0].subscription_id == "sub-1"

    def test_no_match(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1", event_types=["order.placed"])
        delivered = bus.publish(_event(event_type="user.created"))
        assert len(delivered) == 0

    def test_wildcard_receives_all(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1")  # wildcard
        delivered = bus.publish(_event(event_type="anything.here"))
        assert len(delivered) == 1

    def test_multiple_subscribers(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1", event_types=["user.created"])
        bus.subscribe("inst-1", "sub-2")  # wildcard
        delivered = bus.publish(_event())
        assert len(delivered) == 2


class TestUnsubscribe:
    def test_unsubscribe(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1")
        bus.unsubscribe("inst-1", "sub-1")
        delivered = bus.publish(_event())
        assert len(delivered) == 0

    def test_unsubscribe_nonexistent(self):
        bus = AppEventBus()
        with pytest.raises(KeyError):
            bus.unsubscribe("inst-1", "nope")


class TestHistory:
    def test_history_newest_first(self):
        bus = AppEventBus()
        bus.publish(_event(event_id="e1"))
        bus.publish(_event(event_id="e2"))
        h = bus.get_history("inst-1")
        assert h[0].event_id == "e2"

    def test_filter_by_type(self):
        bus = AppEventBus()
        bus.publish(_event(event_id="e1", event_type="a"))
        bus.publish(_event(event_id="e2", event_type="b"))
        h = bus.get_history("inst-1", event_type="a")
        assert len(h) == 1

    def test_history_limit(self):
        bus = AppEventBus(history_limit=15)
        for i in range(20):
            bus.publish(_event(event_id=f"e{i}"))
        h = bus.get_history("inst-1")
        assert len(h) == 15


class TestDeliveryCount:
    def test_count(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1")
        bus.publish(_event(event_id="e1"))
        bus.publish(_event(event_id="e2"))
        assert bus.get_delivery_count("inst-1", "sub-1") == 2


class TestIsolation:
    def test_cross_installation(self):
        bus = AppEventBus()
        bus.subscribe("inst-1", "sub-1")
        delivered = bus.publish(_event(installation_id="inst-2"))
        assert len(delivered) == 0
