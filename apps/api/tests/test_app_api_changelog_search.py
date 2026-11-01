"""Tests for App API Changelog Search — index, search, ranking."""

from app.services.app_api_changelog_search import AppAPIChangelogSearch


class TestIndex:
    def test_index(self):
        s = AppAPIChangelogSearch()
        e = s.index("inst-1", "e1", "Dark Mode", "Added dark theme support", "v2.0", ["ui"])
        assert e.title == "Dark Mode"


class TestSearch:
    def test_title_match(self):
        s = AppAPIChangelogSearch()
        s.index("inst-1", "e1", "Dark Mode", "Theme support", "v2.0")
        s.index("inst-1", "e2", "API Changes", "New endpoints", "v2.0")
        results = s.search("inst-1", "dark")
        assert len(results) == 1
        assert results[0].entry.entry_id == "e1"

    def test_content_match(self):
        s = AppAPIChangelogSearch()
        s.index("inst-1", "e1", "Update", "Fixed authentication bug", "v1.5")
        results = s.search("inst-1", "authentication")
        assert len(results) == 1

    def test_title_ranks_higher(self):
        s = AppAPIChangelogSearch()
        s.index("inst-1", "e1", "Auth", "Something else", "v1")
        s.index("inst-1", "e2", "Update", "Auth fix in content", "v2")
        results = s.search("inst-1", "auth")
        assert results[0].entry.entry_id == "e1"

    def test_empty_query(self):
        s = AppAPIChangelogSearch()
        s.index("inst-1", "e1", "Title", "Content", "v1")
        assert s.search("inst-1", "") == []


class TestIsolation:
    def test_cross(self):
        s = AppAPIChangelogSearch()
        s.index("inst-1", "e1", "Title", "Content", "v1")
        assert s.search("inst-2", "title") == []
