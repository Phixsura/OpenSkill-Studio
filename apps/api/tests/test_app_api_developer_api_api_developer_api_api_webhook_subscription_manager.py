import pytest
from app.services.app_api_developer_api_api_developer_api_api_webhook_subscription_manager import AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager

class TestSubscriptionManager:
    def test_subscribe(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        s = m.subscribe("inst-1", "s1", "order.created", "https://hook.com/orders")
        assert s.active is True

    def test_https_required(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        with pytest.raises(ValueError):
            m.subscribe("inst-1", "s1", "t", "http://bad.com")

    def test_unsubscribe(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        m.subscribe("inst-1", "s1", "t", "https://a.com")
        m.unsubscribe("inst-1", "s1")
        assert len(m.by_topic("inst-1", "t")) == 0

    def test_delivery_tracking(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        m.subscribe("inst-1", "s1", "t", "https://a.com")
        for _ in range(9): m.record_delivery("inst-1", "s1", True)
        m.record_delivery("inst-1", "s1", False)
        s = m.all_subscriptions("inst-1")[0]
        assert s.success_rate == 90.0

    def test_by_topic(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        m.subscribe("inst-1", "s1", "order.created", "https://a.com")
        m.subscribe("inst-1", "s2", "user.created", "https://b.com")
        assert len(m.by_topic("inst-1", "order.created")) == 1

    def test_isolation(self):
        m = AppAPIDeveloperAPIApiDeveloperApiApiWebhookSubscriptionManager()
        m.subscribe("inst-1", "s1", "t", "https://a.com")
        assert len(m.all_subscriptions("inst-2")) == 0
