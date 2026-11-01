import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_event_stream import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream, StreamSubscription, StreamEvent,
)

class TestEventStream:
    def test_subscribe_and_publish(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream()
        svc.subscribe("inst-1", StreamSubscription(subscription_id="s1", consumer_id="c1", event_types=["order.created"]))
        matched = svc.publish("inst-1", StreamEvent(event_id="e1", event_type="order.created", data='{"id":"o1"}'))
        assert matched == 1

    def test_no_match(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream()
        svc.subscribe("inst-1", StreamSubscription(subscription_id="s1", consumer_id="c1", event_types=["user.created"]))
        matched = svc.publish("inst-1", StreamEvent(event_id="e1", event_type="order.created", data="{}"))
        assert matched == 0

    def test_unsubscribe(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream()
        svc.subscribe("inst-1", StreamSubscription(subscription_id="s1", consumer_id="c1", event_types=["x"]))
        assert svc.unsubscribe("inst-1", "s1") is True
        assert len(svc.active_subscriptions("inst-1")) == 0

    def test_invalid_transport(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream()
        with pytest.raises(ValueError, match="Invalid transport"):
            svc.subscribe("inst-1", StreamSubscription(subscription_id="s1", consumer_id="c1", event_types=["x"], transport="grpc"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiEventStream()
        svc.subscribe("inst-1", StreamSubscription(subscription_id="s1", consumer_id="c1", event_types=["x"]))
        assert len(svc.list_subscriptions("inst-2")) == 0
