import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_api_webhook_delivery_analytics import (
    AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics, DeliveryMetric,
)

class TestWebhookDeliveryAnalytics:
    def test_analyze(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-01", deliveries=100, successes=95, failures=5, avg_latency_ms=120, success_rate=95))
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-02", deliveries=120, successes=118, failures=2, avg_latency_ms=100, success_rate=98.3))
        analytics = svc.analyze("inst-1", "c1", "w1")
        assert analytics.total_deliveries == 220 and analytics.trend == "improving"

    def test_declining_trend(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-01", deliveries=100, successes=98, failures=2, avg_latency_ms=50, success_rate=98))
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-02", deliveries=100, successes=80, failures=20, avg_latency_ms=200, success_rate=80))
        assert svc.analyze("inst-1", "c1", "w1").trend == "declining"

    def test_empty(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        assert svc.analyze("inst-1", "c1", "w1").total_deliveries == 0

    def test_list_webhooks(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-01", deliveries=10, successes=10, failures=0, avg_latency_ms=50, success_rate=100))
        svc.add_period("inst-1", "c1", "w2", DeliveryMetric(period="2026-06-01", deliveries=5, successes=5, failures=0, avg_latency_ms=30, success_rate=100))
        assert svc.list_webhooks("inst-1", "c1") == ["w1", "w2"]

    def test_overall_rate(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-01", deliveries=50, successes=50, failures=0, avg_latency_ms=50, success_rate=100))
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-02", deliveries=50, successes=40, failures=10, avg_latency_ms=80, success_rate=80))
        assert svc.analyze("inst-1", "c1", "w1").overall_success_rate == 90.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiWebhookDeliveryAnalytics()
        svc.add_period("inst-1", "c1", "w1", DeliveryMetric(period="2026-06-01", deliveries=10, successes=10, failures=0, avg_latency_ms=50, success_rate=100))
        assert svc.analyze("inst-2", "c1", "w1").total_deliveries == 0
