"""Tests for App Changelog Diff — added, removed, modified, nested."""

import pytest

from app.services.app_changelog_diff import AppChangelogDiff


class TestDiff:
    def test_no_changes(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "1.1", {"a": 1}, {"a": 1})
        assert r.has_changes is False
        assert len(r.changes) == 0

    def test_added_field(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "1.1", {}, {"name": "app"})
        assert r.added_count == 1
        assert r.changes[0].path == "name"
        assert r.changes[0].change_type == "added"

    def test_removed_field(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "1.1", {"old": True}, {})
        assert r.removed_count == 1
        assert r.changes[0].change_type == "removed"

    def test_modified_field(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "2.0", {"port": 80}, {"port": 443})
        assert r.modified_count == 1
        assert r.changes[0].old_value == 80
        assert r.changes[0].new_value == 443

    def test_nested_diff(self):
        d = AppChangelogDiff()
        old = {"config": {"timeout": 30, "debug": False}}
        new = {"config": {"timeout": 60, "debug": False}}
        r = d.diff("1.0", "1.1", old, new)
        assert r.modified_count == 1
        assert r.changes[0].path == "config.timeout"

    def test_nested_added(self):
        d = AppChangelogDiff()
        old = {"config": {"a": 1}}
        new = {"config": {"a": 1, "b": 2}}
        r = d.diff("1.0", "1.1", old, new)
        assert r.added_count == 1
        assert r.changes[0].path == "config.b"

    def test_multiple_changes(self):
        d = AppChangelogDiff()
        old = {"a": 1, "b": 2, "c": 3}
        new = {"a": 1, "b": 99, "d": 4}
        r = d.diff("1.0", "2.0", old, new)
        assert r.modified_count == 1  # b changed
        assert r.removed_count == 1  # c removed
        assert r.added_count == 1    # d added


class TestSummarize:
    def test_no_changes(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "1.1", {"a": 1}, {"a": 1})
        assert "No changes" in d.summarize(r)

    def test_with_changes(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "2.0", {"a": 1}, {"a": 2, "b": 3})
        s = d.summarize(r)
        assert "1.0 → 2.0" in s
        assert "1 added" in s
        assert "1 modified" in s


class TestValidation:
    def test_missing_from_version(self):
        d = AppChangelogDiff()
        with pytest.raises(ValueError, match="from_version"):
            d.diff("", "1.1", {}, {})

    def test_missing_to_version(self):
        d = AppChangelogDiff()
        with pytest.raises(ValueError, match="to_version"):
            d.diff("1.0", "", {}, {})


class TestHasChanges:
    def test_property(self):
        d = AppChangelogDiff()
        r = d.diff("1.0", "1.1", {"x": 1}, {"x": 2})
        assert r.has_changes is True
