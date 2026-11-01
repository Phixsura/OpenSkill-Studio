import pytest
from datetime import datetime, timedelta
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_webhook_event_deduplicator import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator,
)

class TestWebhookEventDeduplicator:
    def _now(self):
        return datetime(2026, 6, 1, 12, 0, 0)

    def test_first_event_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator()
        result = svc.check_and_record("inst-1", "c1", "e1", "order.created", '{"id":"123"}', self._now())
        assert not result.is_duplicate

    def test_duplicate_detected(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator()
        svc.check_and_record("inst-1", "c1", "e1", "order.created", '{"id":"123"}', self._now())
        result = svc.check_and_record("inst-1", "c1", "e2", "order.created", '{"id":"123"}', self._now() + timedelta(minutes=5))
        assert result.is_duplicate and result.original_event_id == "e1"

    def test_different_payload_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator()
        svc.check_and_record("inst-1", "c1", "e1", "order.created", '{"id":"123"}', self._now())
        result = svc.check_and_record("inst-1", "c1", "e2", "order.created", '{"id":"456"}', self._now())
        assert not result.is_duplicate

    def test_expired_not_duplicate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator(ttl_hours=1)
        svc.check_and_record("inst-1", "c1", "e1", "order.created", '{"id":"123"}', self._now())
        result = svc.check_and_record("inst-1", "c1", "e2", "order.created", '{"id":"123"}', self._now() + timedelta(hours=2))
        assert not result.is_duplicate

    def test_cleanup(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator(ttl_hours=1)
        svc.check_and_record("inst-1", "c1", "e1", "x", "y", self._now())
        removed = svc.cleanup("inst-1", self._now() + timedelta(hours=2))
        assert removed == 1

    def test_fingerprint_deterministic(self):
        fp1 = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator.compute_fingerprint("order.created", '{"id":"123"}')
        fp2 = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator.compute_fingerprint("order.created", '{"id":"123"}')
        assert fp1 == fp2 and len(fp1) == 24

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiWebhookEventDeduplicator()
        svc.check_and_record("inst-1", "c1", "e1", "x", "y", self._now())
        assert svc.stats("inst-2")["tracked_fingerprints"] == 0
