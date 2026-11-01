import pytest
from app.services.app_api_sdk_changelog import AppAPISDKChangelog

class TestSDKChangelog:
    def test_add(self):
        s = AppAPISDKChangelog()
        e = s.add_entry("inst-1", "2.0.0", ["New auth flow", "Updated types"], breaking=True)
        assert e.breaking is True

    def test_latest(self):
        s = AppAPISDKChangelog()
        s.add_entry("inst-1", "1.0.0", ["Initial"])
        s.add_entry("inst-1", "2.0.0", ["Updated"])
        assert s.latest("inst-1").version == "2.0.0"

    def test_breaking(self):
        s = AppAPISDKChangelog()
        s.add_entry("inst-1", "1.0", ["A"])
        s.add_entry("inst-1", "2.0", ["B"], breaking=True)
        assert len(s.breaking_versions("inst-1")) == 1

    def test_isolation(self):
        s = AppAPISDKChangelog()
        s.add_entry("inst-1", "1.0", ["A"])
        assert s.list_entries("inst-2") == []
