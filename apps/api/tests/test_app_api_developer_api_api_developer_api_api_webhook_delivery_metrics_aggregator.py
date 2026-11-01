from app.services.app_api_developer_api_api_developer_api_api_webhook_delivery_metrics_aggregator import AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator

class TestDeliveryMetricsAggregator:
    def test_record(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator()
        m = a.record("inst-1", "2025-01", 10000, 9900, 100, 50, 45.0, 5242880)
        assert m.success_rate == 99.0
        assert m.retry_rate == 0.5

    def test_trend(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator()
        a.record("inst-1", "2025-02", 5000, 4900, 100, 20, 50, 1000000)
        a.record("inst-1", "2025-01", 4000, 3800, 200, 10, 60, 800000)
        trend = a.trend("inst-1")
        assert trend[0].period == "2025-01"

    def test_worst_period(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator()
        a.record("inst-1", "2025-01", 1000, 999, 1, 0, 30, 100000)
        a.record("inst-1", "2025-02", 1000, 800, 200, 50, 100, 200000)
        worst = a.worst_period("inst-1")
        assert worst.period == "2025-02"

    def test_isolation(self):
        a = AppAPIDeveloperAPIApiDeveloperApiApiWebhookDeliveryMetricsAggregator()
        a.record("inst-1", "2025-01", 1000, 1000, 0, 0, 30, 100000)
        assert a.worst_period("inst-2") is None
