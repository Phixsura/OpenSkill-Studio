from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_delivery_metrics import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics

class TestWebhookDeliveryMetrics:
    def test_record_and_rates(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics()
        svc.record("inst-1", "c1", True, 50.0)
        svc.record("inst-1", "c1", False, 200.0, retried=True)
        m = svc.get_metrics("inst-1", "c1")
        assert m.success_rate == 50.0
        assert m.avg_latency_ms == 125.0
        assert m.retry_rate == 50.0
        assert m.max_latency_ms == 200.0

    def test_worst_performers(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics()
        for _ in range(10): svc.record("inst-1", "good", True, 10)
        for _ in range(5): svc.record("inst-1", "bad", True, 10)
        for _ in range(5): svc.record("inst-1", "bad", False, 500)
        worst = svc.worst_performers("inst-1", 1)
        assert worst[0].consumer_id == "bad"

    def test_no_data(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics()
        assert svc.get_metrics("inst-1", "c1") is None

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookDeliveryMetrics()
        svc.record("inst-1", "c1", True, 10)
        assert len(svc.list_metrics("inst-2")) == 0
