from app.services.app_api_developer_api_webhook_summary_report import AppAPIDeveloperAPIWebhookSummaryReport

class TestSummaryReport:
    def test_generate(self):
        r = AppAPIDeveloperAPIWebhookSummaryReport()
        rpt = r.generate("inst-1", "r1", "2024-01", 10000, 9500, 95.0, 120, "push", "https://a.com")
        assert rpt.success_rate == 95.0

    def test_isolation(self):
        r = AppAPIDeveloperAPIWebhookSummaryReport()
        r.generate("inst-1", "r1", "2024-01", 100, 95, 95, 50)
        assert r.list_reports("inst-2") == []
