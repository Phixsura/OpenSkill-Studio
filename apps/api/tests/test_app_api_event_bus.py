"""Tests for App API Event Bus — topics, subscribe, publish."""

import pytest
from app.services.app_api_event_bus import AppAPIEventBus


class TestTopic:
    def test_create(self):
        b = AppAPIEventBus()
        t = b.create_topic("inst-1", "t1", "User Events")
        assert t.publish_count == 0

    def test_duplicate(self):
        b = AppAPIEventBus()
        b.create_topic("inst-1", "t1", "A")
        with pytest.raises(ValueError):
            b.create_topic("inst-1", "t1", "B")


class TestPubSub:
    def test_subscribe_publish(self):
        b = AppAPIEventBus()
        b.create_topic("inst-1", "t1", "Events")
        b.subscribe("inst-1", "s1", "t1", "https://a.com")
        b.subscribe("inst-1", "s2", "t1", "https://b.com")
        count = b.publish("inst-1", "t1")
        assert count == 2

    def test_publish_tracks(self):
        b = AppAPIEventBus()
        b.create_topic("inst-1", "t1", "Events")
        b.publish("inst-1", "t1")
        assert b.list_topics("inst-1")[0].publish_count == 1


class TestIsolation:
    def test_cross(self):
        b = AppAPIEventBus()
        b.create_topic("inst-1", "t1", "Events")
        assert b.list_topics("inst-2") == []
