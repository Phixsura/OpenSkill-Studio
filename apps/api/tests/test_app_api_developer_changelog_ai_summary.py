import pytest
from app.services.app_api_developer_changelog_ai_summary import AppAPIDeveloperChangelogAISummary

class TestAISummary:
    def test_generate(self):
        a = AppAPIDeveloperChangelogAISummary()
        s = a.generate("inst-1", "s1", "v3.0", "Major release with dark mode and API v2", ["Dark mode", "API v2", "Performance improvements"])
        assert len(s.key_points) == 3

    def test_get_version(self):
        a = AppAPIDeveloperChangelogAISummary()
        a.generate("inst-1", "s1", "v3.0", "Summary", ["Point"])
        assert a.get_for_version("inst-1", "v3.0") is not None
        assert a.get_for_version("inst-1", "v2.0") is None

    def test_empty_summary(self):
        a = AppAPIDeveloperChangelogAISummary()
        with pytest.raises(ValueError):
            a.generate("inst-1", "s1", "v1", "  ", [])

    def test_isolation(self):
        a = AppAPIDeveloperChangelogAISummary()
        a.generate("inst-1", "s1", "v1", "S", [])
        assert a.list_summaries("inst-2") == []
