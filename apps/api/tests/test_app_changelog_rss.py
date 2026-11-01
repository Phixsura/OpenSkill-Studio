"""Tests for App Changelog RSS — configure, add items, generate feed."""

import pytest

from app.services.app_changelog_rss import AppChangelogRSS


class TestConfigure:
    def test_configure(self):
        r = AppChangelogRSS()
        config = r.configure("inst-1", "My App Changelog", "https://example.com", "Updates")
        assert config.title == "My App Changelog"


class TestGenerate:
    def test_generate(self):
        r = AppChangelogRSS()
        r.configure("inst-1", "Changelog", "https://example.com", "Updates")
        r.add_item("inst-1", "i1", "v2.0 Release", "New features", "v2.0")
        xml = r.generate_rss("inst-1")
        assert "<rss" in xml
        assert "<title>v2.0 Release</title>" in xml

    def test_html_escape(self):
        r = AppChangelogRSS()
        r.configure("inst-1", "Log", "https://example.com", "Desc")
        r.add_item("inst-1", "i1", "Fix <script>alert(1)</script>", "Desc & more", "v1")
        xml = r.generate_rss("inst-1")
        assert "<script>" not in xml
        assert "&lt;script&gt;" in xml
        assert "&amp;" in xml

    def test_not_configured(self):
        r = AppChangelogRSS()
        with pytest.raises(ValueError, match="not configured"):
            r.generate_rss("inst-1")

    def test_limit(self):
        r = AppChangelogRSS()
        r.configure("inst-1", "Log", "https://example.com", "Desc")
        for i in range(5):
            r.add_item("inst-1", f"i{i}", f"v{i}", "desc", f"v{i}")
        xml = r.generate_rss("inst-1", limit=2)
        assert xml.count("<item>") == 2


class TestIsolation:
    def test_cross(self):
        r = AppChangelogRSS()
        r.configure("inst-1", "Log", "https://example.com", "Desc")
        r.add_item("inst-1", "i1", "Title", "Desc", "v1")
        assert r.item_count("inst-2") == 0
