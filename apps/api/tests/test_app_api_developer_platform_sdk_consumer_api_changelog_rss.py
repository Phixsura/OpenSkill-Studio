"""Tests for Consumer API Changelog RSS service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_changelog_rss import (
    ChangelogFeed, FeedEntry,
)


class TestChangelogFeed:
    def test_add_and_generate_rss(self):
        svc = ChangelogFeed()
        svc.configure("My API Changelog", "https://api.example.com/changelog")
        svc.add_entry(FeedEntry("e1", "New Search API", "Added full-text search", "2.0.0"))
        rss = svc.generate_rss()
        assert '<?xml version="1.0"' in rss
        assert "<title>My API Changelog</title>" in rss
        assert "New Search API" in rss

    def test_generate_atom(self):
        svc = ChangelogFeed()
        svc.configure("API Updates")
        svc.add_entry(FeedEntry("e1", "Bug Fix", "Fixed auth issue", "1.0.1", category="bugfix"))
        atom = svc.generate_atom()
        assert "Atom" in atom
        assert "Bug Fix" in atom
        assert 'category term="bugfix"' in atom

    def test_entries_sorted_by_date(self):
        svc = ChangelogFeed()
        svc.add_entry(FeedEntry("e1", "Old", "old", "1.0", published_at="2024-01-01"))
        svc.add_entry(FeedEntry("e2", "New", "new", "2.0", published_at="2024-06-01"))
        entries = svc.get_entries()
        assert entries[0]["title"] == "New"

    def test_filter_by_category(self):
        svc = ChangelogFeed()
        svc.add_entry(FeedEntry("e1", "Feature", "new", "1.0", category="feature"))
        svc.add_entry(FeedEntry("e2", "Bugfix", "fix", "1.0.1", category="bugfix"))
        features = svc.get_entries(category="feature")
        assert len(features) == 1

    def test_duplicate_entry(self):
        svc = ChangelogFeed()
        svc.add_entry(FeedEntry("e1", "A", "a", "1.0"))
        with pytest.raises(ValueError):
            svc.add_entry(FeedEntry("e1", "B", "b", "2.0"))

    def test_empty_title(self):
        svc = ChangelogFeed()
        with pytest.raises(ValueError):
            svc.add_entry(FeedEntry("e1", "", "content", "1.0"))

    def test_stats(self):
        svc = ChangelogFeed()
        svc.add_entry(FeedEntry("e1", "A", "a", "1.0", category="feature"))
        svc.add_entry(FeedEntry("e2", "B", "b", "1.1", category="bugfix"))
        svc.add_entry(FeedEntry("e3", "C", "c", "2.0", category="feature"))
        stats = svc.get_stats()
        assert stats["total_entries"] == 3
        assert stats["by_category"]["feature"] == 2

    def test_limit(self):
        svc = ChangelogFeed()
        for i in range(10):
            svc.add_entry(FeedEntry(f"e{i}", f"Entry {i}", "content", f"1.{i}"))
        entries = svc.get_entries(limit=3)
        assert len(entries) == 3

    def test_isolation(self):
        a, b = ChangelogFeed(), ChangelogFeed()
        a.add_entry(FeedEntry("e1", "A", "a", "1.0"))
        assert b.get_stats()["total_entries"] == 0
