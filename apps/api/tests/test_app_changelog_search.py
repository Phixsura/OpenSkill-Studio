"""Tests for App Changelog Search — indexing, search, scoring, filters."""

import pytest

from app.services.app_changelog_search import AppChangelogSearch


@pytest.fixture
def search():
    s = AppChangelogSearch()
    s.index_entry("inst-1", "e1", "2.0.0", "New dashboard API", "Redesigned dashboard with new endpoints", "added")
    s.index_entry("inst-1", "e2", "2.0.0", "Fixed login bug", "Resolved redirect issue on login page", "fixed")
    s.index_entry("inst-1", "e3", "1.0.0", "Initial release", "First version of the API", "added")
    return s


class TestIndex:
    def test_index(self, search):
        assert search.entry_count("inst-1") == 3

    def test_missing_id(self):
        s = AppChangelogSearch()
        with pytest.raises(ValueError):
            s.index_entry("inst-1", "", "1.0", "title", "desc")


class TestSearch:
    def test_basic_search(self, search):
        results = search.search("inst-1", "dashboard")
        assert len(results) >= 1
        assert results[0].entry.title == "New dashboard API"

    def test_title_weighted_higher(self, search):
        results = search.search("inst-1", "API")
        # "New dashboard API" has API in title (3 pts), "Initial release" has API in desc (1 pt)
        assert results[0].entry.entry_id == "e1"

    def test_multi_term(self, search):
        results = search.search("inst-1", "login bug")
        assert len(results) >= 1
        assert results[0].entry.entry_id == "e2"

    def test_no_results(self, search):
        results = search.search("inst-1", "nonexistent")
        assert len(results) == 0

    def test_empty_query(self, search):
        with pytest.raises(ValueError, match="query"):
            search.search("inst-1", "")


class TestFilters:
    def test_filter_by_version(self, search):
        results = search.search("inst-1", "API", version="1.0.0")
        assert len(results) == 1
        assert results[0].entry.version == "1.0.0"

    def test_filter_by_category(self, search):
        results = search.search("inst-1", "API", category="added")
        assert all(r.entry.category == "added" for r in results)


class TestScoring:
    def test_matched_fields(self, search):
        results = search.search("inst-1", "dashboard")
        assert "title" in results[0].matched_fields

    def test_limit(self, search):
        results = search.search("inst-1", "API", limit=1)
        assert len(results) == 1


class TestIsolation:
    def test_cross_installation(self, search):
        results = search.search("inst-2", "dashboard")
        assert len(results) == 0
