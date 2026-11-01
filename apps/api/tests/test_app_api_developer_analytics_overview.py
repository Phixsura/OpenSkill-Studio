from app.services.app_api_developer_analytics_overview import AppAPIDeveloperAnalyticsOverview

class TestOverview:
    def test_update(self):
        o = AppAPIDeveloperAnalyticsOverview()
        ov = o.update("inst-1", total_developers=100, total_apps=50, avg_developer_satisfaction=4.5)
        assert ov.total_developers == 100

    def test_default(self):
        o = AppAPIDeveloperAnalyticsOverview()
        assert o.get("inst-1").platform_health_score == 100.0

    def test_isolation(self):
        o = AppAPIDeveloperAnalyticsOverview()
        o.update("inst-1", total_developers=50)
        assert o.get("inst-2").total_developers == 0
