import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_api_consumer_api_api_api_consumer_webhook_history import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory, WebhookDeliveryRecord,
)

class TestConsumerWebhookHistory:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d1", webhook_id="w1", consumer_id="c1", event_type="order.created", url="https://x.com", status_code=200, success=True, latency_ms=50, timestamp=self._now()))
        records = svc.query("inst-1", "c1")
        assert len(records) == 1 and records[0].success

    def test_filter_by_webhook(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d1", webhook_id="w1", consumer_id="c1", event_type="a", url="https://x.com", success=True, timestamp=self._now()))
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d2", webhook_id="w2", consumer_id="c1", event_type="b", url="https://y.com", success=True, timestamp=self._now()))
        assert len(svc.query("inst-1", "c1", webhook_id="w1")) == 1

    def test_filter_failures(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d1", webhook_id="w1", consumer_id="c1", event_type="a", url="https://x.com", success=True, timestamp=self._now()))
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d2", webhook_id="w1", consumer_id="c1", event_type="b", url="https://x.com", success=False, error="timeout", timestamp=self._now()))
        assert len(svc.query("inst-1", "c1", success=False)) == 1

    def test_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d1", webhook_id="w1", consumer_id="c1", event_type="a", url="https://x.com", success=True, latency_ms=100, timestamp=self._now()))
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d2", webhook_id="w1", consumer_id="c1", event_type="b", url="https://x.com", success=False, timestamp=self._now()))
        summary = svc.get_summary("inst-1", "c1")
        assert summary.total_deliveries == 2 and summary.success_rate_pct == 50.0

    def test_empty_summary(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        summary = svc.get_summary("inst-1", "c1")
        assert summary.total_deliveries == 0 and summary.success_rate_pct == 100

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory()
        svc.record("inst-1", WebhookDeliveryRecord(delivery_id="d1", webhook_id="w1", consumer_id="c1", event_type="a", url="https://x.com", timestamp=self._now()))
        assert len(svc.query("inst-2", "c1")) == 0
