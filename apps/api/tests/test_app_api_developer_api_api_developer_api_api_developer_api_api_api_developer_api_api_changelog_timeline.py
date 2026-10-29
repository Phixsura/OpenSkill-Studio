from app.services.app_api_developer_api_api_developer_api_api_developer_api_api_api_developer_api_api_changelog_timeline import AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline

class TestChangelogTimeline:
    def test_add(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline()
        e = t.add("inst-1", "e1", "v2.0", "New users endpoint", "feature")
        assert e.change_type == "feature"

    def test_timeline_order(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline()
        t.add("inst-1", "e1", "v1.0", "First", "feature")
        t.add("inst-1", "e2", "v2.0", "Second", "fix")
        tl = t.timeline("inst-1")
        assert tl[0].entry_id == "e2"

    def test_by_type(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline()
        t.add("inst-1", "e1", "v1.0", "A", "feature")
        t.add("inst-1", "e2", "v1.0", "B", "fix")
        assert len(t.by_type("inst-1", "feature")) == 1

    def test_type_counts(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline()
        t.add("inst-1", "e1", "v1.0", "A", "feature")
        t.add("inst-1", "e2", "v1.0", "B", "feature")
        t.add("inst-1", "e3", "v1.0", "C", "breaking")
        assert t.type_counts("inst-1") == {"feature": 2, "breaking": 1}

    def test_isolation(self):
        t = AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiChangelogTimeline()
        t.add("inst-1", "e1", "v1.0", "A", "feature")
        assert len(t.timeline("inst-2")) == 0
