from app.services.app_api_developer_api_changelog_analytics import AppAPIDeveloperChangelogAnalytics

class TestChangelogAnalytics:
    def test_engagement(self):
        a = AppAPIDeveloperChangelogAnalytics()
        ca = a.update("inst-1", total_views=1000, total_reactions=50, total_comments=20, total_bookmarks=30)
        assert ca.engagement_rate == 10.0

    def test_default(self):
        a = AppAPIDeveloperChangelogAnalytics()
        assert a.get("inst-1").engagement_rate == 0.0

    def test_isolation(self):
        a = AppAPIDeveloperChangelogAnalytics()
        a.update("inst-1", total_views=500)
        assert a.get("inst-2").total_views == 0
