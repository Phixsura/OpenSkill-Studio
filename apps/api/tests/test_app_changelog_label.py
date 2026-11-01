"""Tests for App Changelog Label — labels, entries, queries, stats."""

import pytest

from app.services.app_changelog_label import AppChangelogLabel


class TestDefineLabel:
    def test_define(self):
        l = AppChangelogLabel()
        label = l.define_label("inst-1", "feat", "Feature", "type", color="#22c55e")
        assert label.name == "Feature"
        assert label.category == "type"

    def test_invalid_category(self):
        l = AppChangelogLabel()
        with pytest.raises(ValueError, match="category"):
            l.define_label("inst-1", "x", "X", "invalid")

    def test_duplicate(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "feat", "Feature", "type")
        with pytest.raises(ValueError, match="already exists"):
            l.define_label("inst-1", "feat", "Feature2", "type")


class TestEntries:
    def test_add(self):
        l = AppChangelogLabel()
        e = l.add_entry("inst-1", "e1", "1.0.0", "New API endpoint")
        assert e.entry_id == "e1"

    def test_apply_label(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "feat", "Feature", "type")
        l.add_entry("inst-1", "e1", "1.0.0", "New API")
        e = l.apply_label("inst-1", "e1", "feat")
        assert "feat" in e.labels

    def test_apply_unknown_label(self):
        l = AppChangelogLabel()
        l.add_entry("inst-1", "e1", "1.0.0", "X")
        with pytest.raises(KeyError, match="Label"):
            l.apply_label("inst-1", "e1", "nope")

    def test_remove_label(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "feat", "Feature", "type")
        l.add_entry("inst-1", "e1", "1.0.0", "X", labels=["feat"])
        e = l.remove_label("inst-1", "e1", "feat")
        assert "feat" not in e.labels

    def test_idempotent_apply(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "feat", "Feature", "type")
        l.add_entry("inst-1", "e1", "1.0.0", "X")
        l.apply_label("inst-1", "e1", "feat")
        l.apply_label("inst-1", "e1", "feat")
        e = l._get_entry("inst-1", "e1")
        assert e.labels.count("feat") == 1


class TestQuery:
    def test_find_by_label(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "bug", "Bug Fix", "type")
        l.add_entry("inst-1", "e1", "1.0.0", "Fix A", labels=["bug"])
        l.add_entry("inst-1", "e2", "1.0.0", "Fix B", labels=["bug"])
        l.add_entry("inst-1", "e3", "1.0.0", "Feature C")
        results = l.find_by_label("inst-1", "bug")
        assert len(results) == 2

    def test_label_stats(self):
        l = AppChangelogLabel()
        l.add_entry("inst-1", "e1", "1.0.0", "A", labels=["feat", "api"])
        l.add_entry("inst-1", "e2", "1.0.0", "B", labels=["feat"])
        stats = l.get_label_stats("inst-1")
        assert stats["feat"] == 2
        assert stats["api"] == 1


class TestListLabels:
    def test_filter_category(self):
        l = AppChangelogLabel()
        l.define_label("inst-1", "feat", "Feature", "type")
        l.define_label("inst-1", "api", "API", "scope")
        labels = l.list_labels("inst-1", category="type")
        assert len(labels) == 1


class TestIsolation:
    def test_cross_installation(self):
        l = AppChangelogLabel()
        l.add_entry("inst-1", "e1", "1.0.0", "X", labels=["feat"])
        assert l.find_by_label("inst-2", "feat") == []
