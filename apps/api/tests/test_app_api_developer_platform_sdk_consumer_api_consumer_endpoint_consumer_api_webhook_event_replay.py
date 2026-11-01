import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_webhook_event_replay import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay, ReplayableEvent,
)

class TestWebhookEventReplay:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_store_and_replay(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e1", event_type="order.created", payload={"id": "123"}, original_status=200, original_at=self._now(), webhook_url="https://hook.example.com"))
        result = svc.replay("inst-1", "c1", "e1", self._now())
        assert result.replay_status == 200 and not result.diff_detected

    def test_replay_not_found(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        with pytest.raises(ValueError, match="not found"):
            svc.replay("inst-1", "c1", "missing", self._now())

    def test_replay_batch(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e1", event_type="a", payload={}, original_status=200, original_at=self._now(), webhook_url="https://x.com"))
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e2", event_type="b", payload={}, original_status=200, original_at=self._now(), webhook_url="https://x.com"))
        results = svc.replay_batch("inst-1", "c1", ["e1", "e2", "missing"], self._now())
        assert len(results) == 2

    def test_filter_by_type(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e1", event_type="order.created", payload={}, original_status=200, original_at=self._now(), webhook_url="https://x.com"))
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e2", event_type="user.updated", payload={}, original_status=200, original_at=self._now(), webhook_url="https://x.com"))
        events = svc.get_stored_events("inst-1", "c1", event_type="order.created")
        assert len(events) == 1

    def test_https_required(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        with pytest.raises(ValueError, match="HTTPS"):
            svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e1", event_type="x", payload={}, original_status=200, original_at=self._now(), webhook_url="http://insecure.com"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiWebhookEventReplay()
        svc.store_event("inst-1", "c1", ReplayableEvent(event_id="e1", event_type="x", payload={}, original_status=200, original_at=self._now(), webhook_url="https://x.com"))
        assert len(svc.get_stored_events("inst-2", "c1")) == 0
