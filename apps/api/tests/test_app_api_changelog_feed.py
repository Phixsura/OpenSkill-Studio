"""Tests for App API Changelog Feed — add, paginate, filter."""

import pytest

from app.services.app_api_changelog_feed import AppAPIChangelogFeed


class TestAdd:
    def test_add(self):
        f = AppAPIChangelogFeed()
        e = f.add_entry("inst-1", "e1", "v2.0", "New Release", "Major update")
        assert e.version == "v2.0"


class TestPaginate:
    def test_first_page(self):
        f = AppAPIChangelogFeed()
        for i in range(15):
            f.add_entry("inst-1", f"e{i}", f"v{i}", f"Title {i}", "Summary")
        result = f.list_entries("inst-1", page=1, page_size=10)
        assert len(result["items"]) == 10
        assert result["total"] == 15
        assert result["pages"] == 2

    def test_second_page(self):
        f = AppAPIChangelogFeed()
        for i in range(15):
            f.add_entry("inst-1", f"e{i}", f"v{i}", f"Title {i}", "S")
        result = f.list_entries("inst-1", page=2, page_size=10)
        assert len(result["items"]) == 5


class TestFilter:
    def test_by_version(self):
        f = AppAPIChangelogFeed()
        f.add_entry("inst-1", "e1", "v1.0", "A", "S")
        f.add_entry("inst-1", "e2", "v2.0", "B", "S")
        assert len(f.by_version("inst-1", "v1.0")) == 1

    def test_latest(self):
        f = AppAPIChangelogFeed()
        f.add_entry("inst-1", "e1", "v1.0", "A", "S")
        f.add_entry("inst-1", "e2", "v2.0", "B", "S")
        assert f.latest("inst-1").version == "v2.0"


class TestIsolation:
    def test_cross(self):
        f = AppAPIChangelogFeed()
        f.add_entry("inst-1", "e1", "v1", "T", "S")
        assert f.count("inst-2") == 0
