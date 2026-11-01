from app.services.app_api_developer_api_changelog_summary import AppAPIDeveloperAPIChangelogSummary

class TestSummary:
    def test_update(self):
        s = AppAPIDeveloperAPIChangelogSummary()
        cs = s.update("inst-1", total_versions=25, total_entries=150, breaking_changes=5, total_subscribers=200)
        assert cs.total_versions == 25
        assert cs.breaking_changes == 5

    def test_default(self):
        s = AppAPIDeveloperAPIChangelogSummary()
        assert s.get("inst-1").total_entries == 0

    def test_isolation(self):
        s = AppAPIDeveloperAPIChangelogSummary()
        s.update("inst-1", total_versions=10)
        assert s.get("inst-2").total_versions == 0
