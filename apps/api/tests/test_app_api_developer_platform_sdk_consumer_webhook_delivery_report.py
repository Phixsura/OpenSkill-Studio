import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_webhook_delivery_report import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport, DeliveryPeriod,
)

class TestWebhookDeliveryReport:
    def test_add_and_report(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-01", total_deliveries=100, successful=95, failed=5, avg_latency_ms=120, success_rate_pct=95))
        report = svc.generate_report("inst-1", "c1", "w1")
        assert report.overall_success_rate == 95.0 and len(report.periods) == 1

    def test_trend_improving(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-01", total_deliveries=100, successful=80, failed=20, avg_latency_ms=100, success_rate_pct=80))
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-02", total_deliveries=100, successful=95, failed=5, avg_latency_ms=90, success_rate_pct=95))
        report = svc.generate_report("inst-1", "c1", "w1")
        assert report.trend == "improving"

    def test_trend_declining(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-01", total_deliveries=100, successful=98, failed=2, avg_latency_ms=50, success_rate_pct=98))
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-02", total_deliveries=100, successful=70, failed=30, avg_latency_ms=200, success_rate_pct=70))
        assert svc.generate_report("inst-1", "c1", "w1").trend == "declining"

    def test_empty_report(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        report = svc.generate_report("inst-1", "c1", "missing")
        assert report.overall_success_rate == 100.0

    def test_list_webhooks(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-01", total_deliveries=10, successful=10, failed=0, avg_latency_ms=50, success_rate_pct=100))
        svc.add_period("inst-1", "c1", "w2", DeliveryPeriod(period="2026-06-01", total_deliveries=5, successful=5, failed=0, avg_latency_ms=30, success_rate_pct=100))
        assert svc.list_webhooks("inst-1", "c1") == ["w1", "w2"]

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport()
        svc.add_period("inst-1", "c1", "w1", DeliveryPeriod(period="2026-06-01", total_deliveries=10, successful=10, failed=0, avg_latency_ms=50, success_rate_pct=100))
        assert len(svc.list_webhooks("inst-2", "c1")) == 0
