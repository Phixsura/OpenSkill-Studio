from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_webhook_delivery_report import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport

class TestWebhookDeliveryReport:
    def test_generate(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport()
        rpt = r.generate("inst-1", "r1", "2025-01", 10000, 9950, 50, 45.0, 15)
        assert rpt.success_rate == 99.5
        assert rpt.health_status == "excellent"

    def test_poor_health(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport()
        rpt = r.generate("inst-1", "r1", "2025-01", 1000, 800, 200, 500.0, 5)
        assert rpt.health_status == "poor"

    def test_trend(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport()
        r.generate("inst-1", "r2", "2025-02", 5000, 4900, 100, 50, 10)
        r.generate("inst-1", "r1", "2025-01", 4000, 3800, 200, 60, 8)
        assert r.trend("inst-1")[0].period == "2025-01"

    def test_worst(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport()
        r.generate("inst-1", "r1", "2025-01", 1000, 999, 1, 30, 5)
        r.generate("inst-1", "r2", "2025-02", 1000, 800, 200, 100, 5)
        assert r.worst_period("inst-1").period == "2025-02"

    def test_isolation(self):
        r = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport()
        r.generate("inst-1", "r1", "2025-01", 1000, 1000, 0, 30, 5)
        assert r.worst_period("inst-2") is None
