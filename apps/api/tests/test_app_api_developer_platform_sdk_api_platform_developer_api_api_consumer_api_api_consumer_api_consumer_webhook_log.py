import pytest
from datetime import datetime
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_webhook_log import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog, WebhookLogEntry,
)

class TestConsumerWebhookLog:
    def _now(self):
        return datetime(2026, 6, 1)

    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="order.created", url="https://example.com", response_status=200, success=True, response_time_ms=50, timestamp=self._now()))
        entries = svc.query("inst-1", "c1")
        assert len(entries) == 1 and entries[0].success

    def test_filter_by_event_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="order.created", url="https://x.com", success=True, timestamp=self._now()))
        svc.record("inst-1", WebhookLogEntry(log_id="l2", webhook_id="wh1", consumer_id="c1", event_type="user.updated", url="https://x.com", success=True, timestamp=self._now()))
        entries = svc.query("inst-1", "c1", event_type="order.created")
        assert len(entries) == 1

    def test_header_redaction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        entry = svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", request_headers={"Authorization": "Bearer secret", "Content-Type": "application/json"}, timestamp=self._now()))
        assert entry.request_headers["Authorization"] == "***"
        assert entry.request_headers["Content-Type"] == "application/json"

    def test_failure_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", success=True, timestamp=self._now()))
        svc.record("inst-1", WebhookLogEntry(log_id="l2", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", success=False, timestamp=self._now()))
        assert svc.failure_rate("inst-1", "c1") == 0.5

    def test_avg_response_time(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", success=True, response_time_ms=100, timestamp=self._now()))
        svc.record("inst-1", WebhookLogEntry(log_id="l2", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", success=True, response_time_ms=200, timestamp=self._now()))
        assert svc.avg_response_time("inst-1", "c1") == 150.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", webhook_id="wh1", consumer_id="c1", event_type="e", url="https://x.com", timestamp=self._now()))
        assert len(svc.query("inst-2", "c1")) == 0
