"""Tests for App API Changelog Digest — compile, deliver, filter."""

import pytest
from app.services.app_api_changelog_digest import AppAPIChangelogDigest

ENTRIES = [
    {"title": "Dark mode", "version": "v2.0", "category": "feature"},
    {"title": "Bug fix", "version": "v2.0.1", "category": "fix"},
]


class TestCompile:
    def test_compile(self):
        d = AppAPIChangelogDigest()
        digest = d.compile("inst-1", "d1", "weekly", "2024-W03", ENTRIES)
        assert digest.entry_count == 2

    def test_invalid_period(self):
        d = AppAPIChangelogDigest()
        with pytest.raises(ValueError):
            d.compile("inst-1", "d1", "yearly", "2024", [])


class TestDeliver:
    def test_mark_delivered(self):
        d = AppAPIChangelogDigest()
        d.compile("inst-1", "d1", "weekly", "2024-W03", ENTRIES)
        digest = d.mark_delivered("inst-1", "d1")
        assert digest.delivered is True


class TestFilter:
    def test_by_period(self):
        d = AppAPIChangelogDigest()
        d.compile("inst-1", "d1", "weekly", "W03", ENTRIES)
        d.compile("inst-1", "d2", "daily", "01-15", ENTRIES)
        assert len(d.list_digests("inst-1", period="weekly")) == 1


class TestIsolation:
    def test_cross(self):
        d = AppAPIChangelogDigest()
        d.compile("inst-1", "d1", "weekly", "W03", ENTRIES)
        assert d.list_digests("inst-2") == []
