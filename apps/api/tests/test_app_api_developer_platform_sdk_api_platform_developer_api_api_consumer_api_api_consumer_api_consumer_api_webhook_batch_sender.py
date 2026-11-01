import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_webhook_batch_sender import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender, BatchConfig, PendingEvent,
)

class TestConsumerApiWebhookBatchSender:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_add_and_flush(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id="e1", event_type="order.created", payload={"id": "1"}, received_at=self._now()))
        svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id="e2", event_type="order.updated", payload={"id": "1"}, received_at=self._now()))
        delivery = svc.flush("inst-1", "c1", "w1", self._now())
        assert delivery is not None and len(delivery.events) == 2

    def test_flush_on_max_size(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        svc.configure("inst-1", BatchConfig(consumer_id="c1", webhook_id="w1", max_batch_size=3))
        for i in range(3):
            svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id=f"e{i}", event_type="x", payload={}, received_at=self._now()))
        assert svc.should_flush("inst-1", "c1", "w1", self._now())

    def test_flush_on_timeout(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        svc.configure("inst-1", BatchConfig(consumer_id="c1", webhook_id="w1", max_wait_seconds=5))
        svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id="e1", event_type="x", payload={}, received_at=self._now()))
        assert not svc.should_flush("inst-1", "c1", "w1", self._now() + timedelta(seconds=3))
        assert svc.should_flush("inst-1", "c1", "w1", self._now() + timedelta(seconds=6))

    def test_empty_flush(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        assert svc.flush("inst-1", "c1", "w1", self._now()) is None

    def test_pending_count(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id="e1", event_type="x", payload={}, received_at=self._now()))
        assert svc.get_pending_count("inst-1", "c1", "w1") == 1
        svc.flush("inst-1", "c1", "w1", self._now())
        assert svc.get_pending_count("inst-1", "c1", "w1") == 0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender()
        svc.add_event("inst-1", "c1", "w1", PendingEvent(event_id="e1", event_type="x", payload={}, received_at=self._now()))
        assert svc.get_pending_count("inst-2", "c1", "w1") == 0
