from app.services.app_api_developer_api_changelog_release_tracker import AppAPIDeveloperAPIChangelogReleaseTracker

class TestTracker:
    def test_track(self):
        t = AppAPIDeveloperAPIChangelogReleaseTracker()
        r = t.track("inst-1", "v3.0", "2024-01-15", 10, 2)
        assert r.breaking_count == 2

    def test_latest(self):
        t = AppAPIDeveloperAPIChangelogReleaseTracker()
        t.track("inst-1", "v1.0", "2024-01", 5)
        t.track("inst-1", "v2.0", "2024-06", 8)
        assert t.latest("inst-1").version == "v2.0"

    def test_totals(self):
        t = AppAPIDeveloperAPIChangelogReleaseTracker()
        t.track("inst-1", "v1", "2024-01", 5)
        t.track("inst-1", "v2", "2024-06", 10)
        assert t.total_entries("inst-1") == 15
        assert t.release_count("inst-1") == 2

    def test_isolation(self):
        t = AppAPIDeveloperAPIChangelogReleaseTracker()
        t.track("inst-1", "v1", "2024-01", 5)
        assert t.release_count("inst-2") == 0
