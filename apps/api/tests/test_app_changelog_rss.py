"""Tests for App Changelog RSS — feed config, items, XML generation."""

import pytest

from app.services.app_changelog_rss import AppChangelogRSS


class TestConfigureFeed:
    def test_configure(self):
        r = AppChangelogRSS()
        c = r.configure_feed("inst-1", "My App Changelog", "Updates", "https://example.com")
        assert c.title == "My App Changelog"

    def test_missing_title(self):
        r = AppChangelogRSS()
        with pytest.raises(ValueError, match="title"):
            r.configure_feed("inst-1", "", "desc", "https://x.com")

    def test_missing_link(self):
        r = AppChangelogRSS()
        with pytest.raises(ValueError, match="link"):
            r.configure_feed("inst-1", "Title", "desc", "")


class TestAddItem:
    def test_add(self):
        r = AppChangelogRSS()
        item = r.add_item("inst-1", "v2.0 Released", "Major update", "2.0.0", "2026-10-28")
        assert item.version == "2.0.0"
        assert r.item_count("inst-1") == 1


class TestGenerateRSS:
    def test_basic_rss(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "Changelog", "Updates", "https://example.com")
        r.add_item("inst-1", "v1.0", "Initial release", "1.0.0", "2026-01-01")
        r.add_item("inst-1", "v2.0", "Major update", "2.0.0", "2026-06-01")
        xml = r.generate_rss("inst-1")
        assert '<?xml version="1.0"' in xml
        assert "<rss" in xml
        assert "<channel>" in xml
        assert "<title>Changelog</title>" in xml
        assert "v2.0" in xml
        assert "v1.0" in xml

    def test_newest_first(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "CL", "X", "https://x.com")
        r.add_item("inst-1", "First", "A", "1.0", "2026-01-01")
        r.add_item("inst-1", "Second", "B", "2.0", "2026-06-01")
        xml = r.generate_rss("inst-1")
        assert xml.index("Second") < xml.index("First")

    def test_limit(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "CL", "X", "https://x.com")
        for i in range(10):
            r.add_item("inst-1", f"v{i}", f"Release {i}", f"{i}.0", "2026-01-01")
        xml = r.generate_rss("inst-1", limit=3)
        assert xml.count("<item>") == 3

    def test_html_escaping(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "CL", "X", "https://x.com")
        r.add_item("inst-1", "Fix <script> bug", "Removed <b>XSS</b>", "1.0", "2026-01-01")
        xml = r.generate_rss("inst-1")
        assert "<script>" not in xml
        assert "&lt;script&gt;" in xml

    def test_not_configured(self):
        r = AppChangelogRSS()
        with pytest.raises(KeyError):
            r.generate_rss("inst-1")

    def test_empty_feed(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "CL", "X", "https://x.com")
        xml = r.generate_rss("inst-1")
        assert "<item>" not in xml
        assert "<channel>" in xml


class TestIsolation:
    def test_cross_installation(self):
        r = AppChangelogRSS()
        r.configure_feed("inst-1", "CL", "X", "https://x.com")
        r.add_item("inst-1", "V1", "A", "1.0", "2026-01-01")
        assert r.item_count("inst-2") == 0
