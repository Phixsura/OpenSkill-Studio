import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_event_bus import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus, EventSubscription, Event,
)

class TestConsumerApiEventBus:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_exact_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="order.created", callback_url="https://hook.example.com"))
        deliveries = svc.publish("inst-1", Event(event_id="e1", event_type="order.created", source="api"), now=self._now())
        assert len(deliveries) == 1

    def test_wildcard_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="order.*"))
        deliveries = svc.publish("inst-1", Event(event_id="e1", event_type="order.updated", source="api"), now=self._now())
        assert len(deliveries) == 1

    def test_global_wildcard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="*"))
        deliveries = svc.publish("inst-1", Event(event_id="e1", event_type="anything", source="api"), now=self._now())
        assert len(deliveries) == 1

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="user.created"))
        deliveries = svc.publish("inst-1", Event(event_id="e1", event_type="order.created", source="api"), now=self._now())
        assert len(deliveries) == 0

    def test_unsubscribe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="*"))
        svc.unsubscribe("inst-1", "s1")
        assert len(svc.list_subscriptions("inst-1")) == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEventBus()
        svc.subscribe("inst-1", EventSubscription(subscription_id="s1", consumer_id="c1", event_pattern="*"))
        deliveries = svc.publish("inst-2", Event(event_id="e1", event_type="test", source="api"), now=self._now())
        assert len(deliveries) == 0
