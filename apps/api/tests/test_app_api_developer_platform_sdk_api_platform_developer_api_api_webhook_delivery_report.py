from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_webhook_delivery_report import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport

class TestWebhookDeliveryReport:
    def test_record_and_report(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport()
        svc.record_delivery("inst-1", "c1", True, 50.0, payload_bytes=1024)
        svc.record_delivery("inst-1", "c1", False, 200.0, retried=True, payload_bytes=512)
        report = svc.generate_report("inst-1", "c1", "2024-01")
        assert report.metrics.total_deliveries == 2
        assert report.metrics.failed == 1

    def test_success_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport()
        svc.record_delivery("inst-1", "c1", True, 10)
        svc.record_delivery("inst-1", "c1", True, 20)
        svc.record_delivery("inst-1", "c1", False, 30)
        assert svc.success_rate("inst-1", "c1") == 66.7

    def test_overall(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport()
        svc.record_delivery("inst-1", "c1", True, 50)
        svc.record_delivery("inst-1", "c2", True, 100)
        overall = svc.overall_metrics("inst-1")
        assert overall.total_deliveries == 2

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiWebhookDeliveryReport()
        svc.record_delivery("inst-1", "c1", True, 10)
        assert len(svc.list_consumers("inst-2")) == 0
