from app.services.app_api_developer_api_changelog_widget_analytics import AppAPIDeveloperAPIChangelogWidgetAnalytics

class TestAnalytics:
    def test_ctr(self):
        a = AppAPIDeveloperAPIChangelogWidgetAnalytics()
        wa = a.update("inst-1", total_impressions=1000, total_clicks=50, entries_read=30)
        assert wa.ctr == 5.0
        assert wa.read_rate == 60.0

    def test_default(self):
        a = AppAPIDeveloperAPIChangelogWidgetAnalytics()
        assert a.get("inst-1").total_impressions == 0

    def test_isolation(self):
        a = AppAPIDeveloperAPIChangelogWidgetAnalytics()
        a.update("inst-1", total_impressions=100)
        assert a.get("inst-2").total_impressions == 0
