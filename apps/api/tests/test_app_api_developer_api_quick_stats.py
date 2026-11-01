from app.services.app_api_developer_api_quick_stats import AppAPIDeveloperAPIQuickStats

class TestQuickStats:
    def test_update(self):
        s = AppAPIDeveloperAPIQuickStats()
        qs = s.update("inst-1", requests_today=50000, errors_today=100, active_developers=25)
        assert qs.requests_today == 50000

    def test_default(self):
        s = AppAPIDeveloperAPIQuickStats()
        assert s.get("inst-1").uptime_today == 100.0

    def test_isolation(self):
        s = AppAPIDeveloperAPIQuickStats()
        s.update("inst-1", requests_today=1000)
        assert s.get("inst-2").requests_today == 0
