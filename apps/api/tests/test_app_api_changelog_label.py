"""Tests for App API Changelog Label — create, assign, filter."""

from app.services.app_api_changelog_label import AppAPIChangelogLabel


class TestLabel:
    def test_create(self):
        l = AppAPIChangelogLabel()
        label = l.create_label("inst-1", "l1", "Bug Fix", "#FF0000")
        assert label.color == "#FF0000"


class TestAssign:
    def test_label_entry(self):
        l = AppAPIChangelogLabel()
        l.create_label("inst-1", "l1", "Bug Fix")
        e = l.label_entry("inst-1", "e1", "Fix login", ["l1"])
        assert "l1" in e.labels

    def test_filter(self):
        l = AppAPIChangelogLabel()
        l.label_entry("inst-1", "e1", "A", ["bug"])
        l.label_entry("inst-1", "e2", "B", ["feature"])
        assert len(l.entries_by_label("inst-1", "bug")) == 1


class TestIsolation:
    def test_cross(self):
        l = AppAPIChangelogLabel()
        l.create_label("inst-1", "l1", "Bug")
        assert l.list_labels("inst-2") == []
