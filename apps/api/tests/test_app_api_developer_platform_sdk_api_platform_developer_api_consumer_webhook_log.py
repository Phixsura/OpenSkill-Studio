from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_webhook_log import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog, WebhookLogEntry,
)

class TestConsumerWebhookLog:
    def test_record_and_query(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", consumer_id="c1", event_type="order.created", endpoint="/hook", status_code=200, duration_ms=50, success=True))
        entries = svc.query("inst-1", consumer_id="c1")
        assert len(entries) == 1

    def test_delivery_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", consumer_id="c1", event_type="e", endpoint="/h", status_code=200, duration_ms=40, success=True))
        svc.record("inst-1", WebhookLogEntry(log_id="l2", consumer_id="c1", event_type="e", endpoint="/h", status_code=500, duration_ms=60, success=False))
        stats = svc.delivery_stats("inst-1")
        assert stats["total"] == 2
        assert stats["success_rate"] == 50.0
        assert stats["avg_duration_ms"] == 50.0

    def test_failed_deliveries(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", consumer_id="c1", event_type="e", endpoint="/h", status_code=200, duration_ms=10, success=True))
        svc.record("inst-1", WebhookLogEntry(log_id="l2", consumer_id="c1", event_type="e", endpoint="/h", status_code=500, duration_ms=10, success=False, error_message="timeout"))
        failed = svc.failed_deliveries("inst-1")
        assert len(failed) == 1

    def test_eviction(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog(max_entries=100)
        for i in range(150): svc.record("inst-1", WebhookLogEntry(log_id=f"l{i}", consumer_id="c1", event_type="e", endpoint="/h", status_code=200, duration_ms=10, success=True))
        assert svc.count("inst-1") == 100

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerWebhookLog()
        svc.record("inst-1", WebhookLogEntry(log_id="l1", consumer_id="c1", event_type="e", endpoint="/h", status_code=200, duration_ms=10, success=True))
        assert svc.count("inst-2") == 0
