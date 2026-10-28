"""Tests for App Changelog Compare — version ranges, categories, breaking."""

import pytest

from app.services.app_changelog_compare import AppChangelogCompare


@pytest.fixture
def cmp():
    c = AppChangelogCompare()
    c.add_entry("inst-1", "e1", "1.0.0", "Init", "added")
    c.add_entry("inst-1", "e2", "1.1.0", "Feature A", "added")
    c.add_entry("inst-1", "e3", "1.1.0", "Fix bug", "fixed")
    c.add_entry("inst-1", "e4", "2.0.0", "New API", "added", breaking=True)
    c.add_entry("inst-1", "e5", "2.0.0", "Removed old", "removed", breaking=True)
    return c


class TestCompare:
    def test_range(self, cmp):
        r = cmp.compare("inst-1", "1.0.0", "2.0.0")
        assert r.total_new == 4  # 1.1.0 (2) + 2.0.0 (2)
        assert r.from_version == "1.0.0"

    def test_single_version(self, cmp):
        r = cmp.compare("inst-1", "1.0.0", "1.1.0")
        assert r.total_new == 2

    def test_categories(self, cmp):
        r = cmp.compare("inst-1", "1.0.0", "2.0.0")
        assert r.category_counts["added"] == 2
        assert r.category_counts["fixed"] == 1

    def test_breaking_count(self, cmp):
        r = cmp.compare("inst-1", "1.0.0", "2.0.0")
        assert r.breaking_count == 2

    def test_no_entries_in_range(self, cmp):
        r = cmp.compare("inst-1", "2.0.0", "3.0.0")
        assert r.total_new == 0

    def test_missing_version(self):
        c = AppChangelogCompare()
        with pytest.raises(ValueError, match="both versions"):
            c.compare("inst-1", "", "1.0.0")


class TestIsolation:
    def test_cross_installation(self, cmp):
        r = cmp.compare("inst-2", "1.0.0", "2.0.0")
        assert r.total_new == 0
