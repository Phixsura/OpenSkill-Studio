"""Tests for App API Changelog — endpoint changes, breaking, counts."""

import pytest

from app.services.app_api_changelog import AppAPIChangelog

CHANGES = [
    {"method": "GET", "path": "/api/v2/users", "change_type": "added", "description": "New users endpoint"},
    {"method": "DELETE", "path": "/api/v1/users", "change_type": "removed", "breaking": True},
    {"method": "PUT", "path": "/api/v1/settings", "change_type": "modified", "description": "New field added"},
    {"method": "GET", "path": "/api/v1/legacy", "change_type": "deprecated"},
]


class TestRecordChanges:
    def test_record(self):
        c = AppAPIChangelog()
        cl = c.record_changes("inst-1", "1.0.0", "2.0.0", CHANGES)
        assert len(cl.changes) == 4

    def test_missing_versions(self):
        c = AppAPIChangelog()
        with pytest.raises(ValueError):
            c.record_changes("inst-1", "", "2.0.0", [])


class TestProperties:
    def test_breaking_count(self):
        c = AppAPIChangelog()
        cl = c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        assert cl.breaking_count == 1

    def test_added_count(self):
        c = AppAPIChangelog()
        cl = c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        assert cl.added_count == 1

    def test_removed_count(self):
        c = AppAPIChangelog()
        cl = c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        assert cl.removed_count == 1


class TestGet:
    def test_get(self):
        c = AppAPIChangelog()
        c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        cl = c.get_changelog("inst-1", "1.0", "2.0")
        assert cl.to_version == "2.0"

    def test_not_found(self):
        c = AppAPIChangelog()
        with pytest.raises(KeyError):
            c.get_changelog("inst-1", "1.0", "9.0")


class TestList:
    def test_list(self):
        c = AppAPIChangelog()
        c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        c.record_changes("inst-1", "2.0", "3.0", CHANGES[:1])
        assert len(c.list_changelogs("inst-1")) == 2


class TestIsolation:
    def test_cross_installation(self):
        c = AppAPIChangelog()
        c.record_changes("inst-1", "1.0", "2.0", CHANGES)
        assert c.list_changelogs("inst-2") == []
