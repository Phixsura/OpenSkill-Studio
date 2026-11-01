"""Tests for App Changelog Category — categories, entries, counts."""

import pytest

from app.services.app_changelog_category import AppChangelogCategory


class TestCategory:
    def test_add(self):
        c = AppChangelogCategory()
        cat = c.add_category("inst-1", "feature", "Features", "✨", 1)
        assert cat.name == "Features"


class TestEntry:
    def test_add_entry(self):
        c = AppChangelogCategory()
        c.add_category("inst-1", "feature", "Features")
        e = c.add_entry("inst-1", "e1", "Add dark mode", "feature", "v2.0")
        assert e.category_id == "feature"

    def test_invalid_category(self):
        c = AppChangelogCategory()
        with pytest.raises(KeyError):
            c.add_entry("inst-1", "e1", "Title", "nonexistent", "v1")


class TestQuery:
    def test_by_category(self):
        c = AppChangelogCategory()
        c.add_category("inst-1", "feature", "Features")
        c.add_category("inst-1", "fix", "Fixes")
        c.add_entry("inst-1", "e1", "Add X", "feature", "v2")
        c.add_entry("inst-1", "e2", "Fix Y", "fix", "v2")
        assert len(c.entries_by_category("inst-1", "feature")) == 1

    def test_counts(self):
        c = AppChangelogCategory()
        c.add_category("inst-1", "feature", "Features", "✨", 1)
        c.add_category("inst-1", "fix", "Fixes", "🐛", 2)
        c.add_entry("inst-1", "e1", "A", "feature", "v1")
        c.add_entry("inst-1", "e2", "B", "feature", "v1")
        c.add_entry("inst-1", "e3", "C", "fix", "v1")
        counts = c.category_counts("inst-1")
        assert counts[0]["count"] == 2
        assert counts[1]["count"] == 1


class TestIsolation:
    def test_cross(self):
        c = AppChangelogCategory()
        c.add_category("inst-1", "feature", "Features")
        assert c.list_categories("inst-2") == []
