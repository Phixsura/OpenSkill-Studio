from app.services.app_api_usage_dashboard import AppAPIUsageDashboard

class TestDashboard:
    def test_update(self):
        d = AppAPIUsageDashboard()
        dash = d.update("inst-1", total_requests=100000, total_errors=500, unique_consumers=50)
        assert dash.error_rate == 0.5

    def test_default(self):
        d = AppAPIUsageDashboard()
        assert d.get("inst-1").total_requests == 0

    def test_isolation(self):
        d = AppAPIUsageDashboard()
        d.update("inst-1", total_requests=1000)
        assert d.get("inst-2").total_requests == 0
