"""Tests for App API Changelog Diff — create, summary, query."""

import pytest

from app.services.app_api_changelog_diff import AppAPIChangelogDiff

CHANGES = [
    {"type": "added", "path": "/api/v2/widgets", "description": "New endpoint"},
    {"type": "modified", "path": "/api/v2/users", "description": "Added email field"},
    {"type": "removed", "path": "/api/v1/legacy"},
]


class TestCreate:
    def test_create(self):
        d = AppAPIChangelogDiff()
        diff = d.create_diff("inst-1", "d1", "v1", "v2", CHANGES)
        assert len(diff.changes) == 3

    def test_summary(self):
        d = AppAPIChangelogDiff()
        diff = d.create_diff("inst-1", "d1", "v1", "v2", CHANGES)
        s = diff.summary
        assert s["added"] == 1
        assert s["removed"] == 1
        assert s["modified"] == 1


class TestQuery:
    def test_get(self):
        d = AppAPIChangelogDiff()
        d.create_diff("inst-1", "d1", "v1", "v2", CHANGES)
        diff = d.get_diff("inst-1", "d1")
        assert diff.from_version == "v1"


class TestIsolation:
    def test_cross(self):
        d = AppAPIChangelogDiff()
        d.create_diff("inst-1", "d1", "v1", "v2", CHANGES)
        assert d.list_diffs("inst-2") == []
