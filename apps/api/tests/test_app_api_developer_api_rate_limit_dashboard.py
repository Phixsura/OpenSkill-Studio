from app.services.app_api_developer_api_rate_limit_dashboard import AppAPIDeveloperAPIRateLimitDashboard

class TestDashboard:
    def test_update(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        rl = d.update("inst-1", total_rules=20, active_rules=18, throttled_requests=500, exhausted_consumers=2)
        assert rl.active_rules == 18

    def test_default(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        assert d.get("inst-1").total_rules == 0

    def test_isolation(self):
        d = AppAPIDeveloperAPIRateLimitDashboard()
        d.update("inst-1", total_rules=10)
        assert d.get("inst-2").total_rules == 0
