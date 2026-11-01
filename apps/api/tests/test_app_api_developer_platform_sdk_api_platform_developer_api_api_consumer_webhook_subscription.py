import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_webhook_subscription import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription, WebhookSubscription,
)

class TestConsumerWebhookSubscription:
    def test_subscribe_and_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription()
        svc.subscribe("inst-1", WebhookSubscription(subscription_id="s1", consumer_id="c1", url="https://hooks.example.com/wh", events=["order.created"]))
        matches = svc.matches("inst-1", "order.created")
        assert len(matches) == 1

    def test_http_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.subscribe("inst-1", WebhookSubscription(subscription_id="s1", consumer_id="c1", url="http://insecure.com/wh", events=["e"]))

    def test_toggle_inactive(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription()
        svc.subscribe("inst-1", WebhookSubscription(subscription_id="s1", consumer_id="c1", url="https://h.com/wh", events=["e"]))
        svc.toggle("inst-1", "s1", False)
        assert len(svc.matches("inst-1", "e")) == 0

    def test_unsubscribe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription()
        svc.subscribe("inst-1", WebhookSubscription(subscription_id="s1", consumer_id="c1", url="https://h.com/wh", events=["e"]))
        assert svc.unsubscribe("inst-1", "s1") is True
        assert len(svc.list_subscriptions("inst-1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerWebhookSubscription()
        svc.subscribe("inst-1", WebhookSubscription(subscription_id="s1", consumer_id="c1", url="https://h.com/wh", events=["e"]))
        assert len(svc.list_subscriptions("inst-2")) == 0
