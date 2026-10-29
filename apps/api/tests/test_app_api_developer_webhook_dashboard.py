from app.services.app_api_developer_webhook_dashboard import AppAPIDeveloperWebhookDashboard

class TestDashboard:
    def test_update(self):
        d = AppAPIDeveloperWebhookDashboard()
        s = d.update("inst-1", total_destinations=10, total_delivered=50000, success_rate=99.2)
        assert s.total_destinations == 10
        assert s.success_rate == 99.2

    def test_default(self):
        d = AppAPIDeveloperWebhookDashboard()
        assert d.get("inst-1").success_rate == 100.0

    def test_isolation(self):
        d = AppAPIDeveloperWebhookDashboard()
        d.update("inst-1", total_destinations=5)
        assert d.get("inst-2").total_destinations == 0
