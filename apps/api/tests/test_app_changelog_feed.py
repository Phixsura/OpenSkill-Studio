"""Tests for App Changelog Feed — publish, query, search, markdown, RSS."""

import pytest

from app.services.app_changelog_feed import (
    AppChangelogFeed,
    ChangeCategory,
    ChangeItem,
    ChangelogEntry,
)


def _entry(version: str = "2.0.0", breaking: bool = False) -> ChangelogEntry:
    items = [
        ChangeItem(ChangeCategory.ADDED, "New dashboard widget"),
        ChangeItem(ChangeCategory.FIXED, "OAuth token refresh bug"),
        ChangeItem(ChangeCategory.CHANGED, "Updated API response format", breaking=breaking),
    ]
    return ChangelogEntry(app_id="app-1", version=version, title=f"Release {version}",
                          items=items, author="dev-team")


class TestPublish:
    def test_publish_entry(self):
        feed = AppChangelogFeed()
        entry = feed.publish(_entry("1.0.0"))
        assert entry.version == "1.0.0"
        assert len(entry.items) == 3

    def test_empty_items_rejected(self):
        feed = AppChangelogFeed()
        with pytest.raises(ValueError, match="at least one"):
            feed.publish(ChangelogEntry("app-1", "1.0.0", "Empty", items=[]))

    def test_get_by_version(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        assert feed.get("app-1", "1.0.0") is not None
        assert feed.get("app-1", "9.9.9") is None


class TestListing:
    def test_list_entries(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        feed.publish(_entry("2.0.0"))
        feed.publish(_entry("3.0.0"))
        entries = feed.list_entries("app-1")
        assert len(entries) == 3
        assert entries[0].version == "3.0.0"  # newest first

    def test_get_latest(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        feed.publish(_entry("2.0.0"))
        latest = feed.get_latest("app-1")
        assert latest.version == "2.0.0"

    def test_latest_empty(self):
        feed = AppChangelogFeed()
        assert feed.get_latest("app-x") is None

    def test_list_limit(self):
        feed = AppChangelogFeed()
        for i in range(10):
            feed.publish(_entry(f"{i}.0.0"))
        assert len(feed.list_entries("app-1", limit=3)) == 3


class TestSearch:
    def test_search_by_title(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        results = feed.search("app-1", "Release 1.0.0")
        assert len(results) == 1

    def test_search_by_item_description(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        results = feed.search("app-1", "dashboard widget")
        assert len(results) == 1

    def test_search_case_insensitive(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        results = feed.search("app-1", "OAUTH")
        assert len(results) == 1

    def test_search_no_match(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        assert feed.search("app-1", "nonexistent feature") == []


class TestBreaking:
    def test_has_breaking(self):
        entry = _entry("2.0.0", breaking=True)
        assert entry.has_breaking is True

    def test_no_breaking(self):
        entry = _entry("1.0.0", breaking=False)
        assert entry.has_breaking is False

    def test_get_breaking_changes(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0", breaking=False))
        feed.publish(_entry("2.0.0", breaking=True))
        feed.publish(_entry("3.0.0", breaking=False))
        breaking = feed.get_breaking_changes("app-1")
        assert len(breaking) == 1
        assert breaking[0].version == "2.0.0"


class TestCategoryCounts:
    def test_counts(self):
        entry = _entry("1.0.0")
        counts = entry.category_counts
        assert counts["added"] == 1
        assert counts["fixed"] == 1
        assert counts["changed"] == 1


class TestMarkdown:
    def test_markdown_output(self):
        entry = _entry("2.0.0")
        md = entry.to_markdown()
        assert "## 2.0.0" in md
        assert "### Added" in md
        assert "dashboard widget" in md
        assert "### Fixed" in md

    def test_breaking_markdown(self):
        entry = _entry("2.0.0", breaking=True)
        md = entry.to_markdown()
        assert "BREAKING" in md


class TestRSS:
    def test_rss_items(self):
        feed = AppChangelogFeed()
        feed.publish(_entry("1.0.0"))
        feed.publish(_entry("2.0.0"))
        items = feed.to_rss_items("app-1")
        assert len(items) == 2
        assert "2.0.0" in items[0]["title"]
        assert "guid" in items[0]
        assert "pubDate" in items[0]

    def test_rss_limit(self):
        feed = AppChangelogFeed()
        for i in range(5):
            feed.publish(_entry(f"{i}.0.0"))
        assert len(feed.to_rss_items("app-1", limit=2)) == 2
