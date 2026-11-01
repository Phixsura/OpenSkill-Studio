from app.services.app_api_webhook_delivery_report import AppAPIWebhookDeliveryReport

class TestReport:
    def test_generate(self):
        r = AppAPIWebhookDeliveryReport()
        report = r.generate("inst-1", "r1", "2024-01", 950, 50, 120.5, "https://a.com", "push")
        assert report.success_rate == 95.0

    def test_get(self):
        r = AppAPIWebhookDeliveryReport()
        r.generate("inst-1", "r1", "2024-01", 100, 0, 50)
        assert r.get("inst-1", "r1").period == "2024-01"

    def test_isolation(self):
        r = AppAPIWebhookDeliveryReport()
        r.generate("inst-1", "r1", "2024-01", 100, 0, 50)
        assert r.list_reports("inst-2") == []
