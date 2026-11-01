from app.services.app_api_developer_dashboard import AppAPIDeveloperDashboard

class TestDashboard:
    def test_update(self):
        d = AppAPIDeveloperDashboard()
        o = d.update("inst-1", total_api_calls=50000, active_developers=25, webhook_success_rate=99.5)
        assert o.total_api_calls == 50000
        assert o.active_developers == 25

    def test_default(self):
        d = AppAPIDeveloperDashboard()
        o = d.get_overview("inst-1")
        assert o.uptime_pct == 100.0
        assert o.total_api_calls == 0

    def test_partial_update(self):
        d = AppAPIDeveloperDashboard()
        d.update("inst-1", active_incidents=2)
        o = d.get_overview("inst-1")
        assert o.active_incidents == 2
        assert o.total_api_calls == 0

    def test_isolation(self):
        d = AppAPIDeveloperDashboard()
        d.update("inst-1", total_api_calls=1000)
        assert d.get_overview("inst-2").total_api_calls == 0
