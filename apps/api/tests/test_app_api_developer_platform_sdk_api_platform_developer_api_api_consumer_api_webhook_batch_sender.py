import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_batch_sender import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender, BatchEvent,
)

class TestWebhookBatchSender:
    def test_create_and_send(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender()
        events = [BatchEvent(event_id="e1", event_type="order.created", payload_size_bytes=500)]
        svc.create_batch("inst-1", "b1", "c1", events)
        b = svc.mark_sent("inst-1", "b1", 200)
        assert b.success is True

    def test_batch_too_large(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender(max_batch_size=5)
        events = [BatchEvent(event_id=f"e{i}", event_type="x") for i in range(10)]
        with pytest.raises(ValueError, match="too large"):
            svc.create_batch("inst-1", "b1", "c1", events)

    def test_payload_too_large(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender(max_payload_bytes=1024)
        events = [BatchEvent(event_id="e1", event_type="x", payload_size_bytes=2000)]
        with pytest.raises(ValueError, match="Payload"):
            svc.create_batch("inst-1", "b1", "c1", events)

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender()
        svc.create_batch("inst-1", "b1", "c1", [BatchEvent("e1", "x")])
        svc.mark_sent("inst-1", "b1", 200)
        svc.create_batch("inst-1", "b2", "c1", [BatchEvent("e2", "y")])
        s = svc.stats("inst-1")
        assert s["success"] == 1 and s["pending"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender()
        svc.create_batch("inst-1", "b1", "c1", [BatchEvent("e1", "x")])
        assert svc.stats("inst-2")["total"] == 0
