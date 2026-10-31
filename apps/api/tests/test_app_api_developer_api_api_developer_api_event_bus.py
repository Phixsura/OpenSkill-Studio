import pytest
from app.services.app_api_developer_api_api_developer_api_event_bus import AppAPIDeveloperAPIApiDeveloperApiEventBus

class TestEventBus:
    def test_subscribe(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        s = b.subscribe("inst-1", "s1", "user.*", "https://hook.com")
        assert s.active is True

    def test_https_required(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        with pytest.raises(ValueError):
            b.subscribe("inst-1", "s1", "user.*", "http://bad.com")

    def test_publish_exact_match(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        b.subscribe("inst-1", "s1", "order.created", "https://a.com")
        e = b.publish("inst-1", "e1", "order.created", 512)
        assert e.subscribers_notified == 1

    def test_publish_wildcard(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        b.subscribe("inst-1", "s1", "user.*", "https://a.com")
        e = b.publish("inst-1", "e1", "user.created", 256)
        assert e.subscribers_notified == 1
        e2 = b.publish("inst-1", "e2", "order.created", 256)
        assert e2.subscribers_notified == 0

    def test_unsubscribe(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        b.subscribe("inst-1", "s1", "*", "https://a.com")
        b.unsubscribe("inst-1", "s1")
        e = b.publish("inst-1", "e1", "anything", 100)
        assert e.subscribers_notified == 0

    def test_isolation(self):
        b = AppAPIDeveloperAPIApiDeveloperApiEventBus()
        b.subscribe("inst-1", "s1", "*", "https://a.com")
        assert len(b.list_subscriptions("inst-2")) == 0
