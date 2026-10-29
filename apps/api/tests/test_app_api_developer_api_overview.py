from app.services.app_api_developer_api_overview import AppAPIDeveloperAPIOverview

class TestOverview:
    def test_update(self):
        o = AppAPIDeveloperAPIOverview()
        ov = o.update("inst-1", total_services=356, total_endpoints=1200, total_developers=500, total_api_calls=10000000)
        assert ov.total_services == 356

    def test_default(self):
        o = AppAPIDeveloperAPIOverview()
        assert o.get("inst-1").uptime_pct == 100.0

    def test_isolation(self):
        o = AppAPIDeveloperAPIOverview()
        o.update("inst-1", total_services=100)
        assert o.get("inst-2").total_services == 0
