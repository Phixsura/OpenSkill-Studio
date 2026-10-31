"""Tests for App Tag Manager — add, remove, find, prefix, counts."""

import pytest

from app.services.app_tag_manager import AppTagManager


class TestAddTags:
    def test_add(self):
        m = AppTagManager()
        r = m.add_tags("inst-1", "project", "p1", ["env:prod", "team:backend"])
        assert r.tags == {"env:prod", "team:backend"}

    def test_add_to_existing(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["a"])
        r = m.add_tags("inst-1", "project", "p1", ["b"])
        assert r.tags == {"a", "b"}

    def test_empty_tags_rejected(self):
        m = AppTagManager()
        with pytest.raises(ValueError, match="at least one"):
            m.add_tags("inst-1", "project", "p1", [])

    def test_invalid_tag(self):
        m = AppTagManager()
        with pytest.raises(ValueError, match="Invalid tag"):
            m.add_tags("inst-1", "project", "p1", [""])


class TestRemoveTags:
    def test_remove(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["a", "b", "c"])
        r = m.remove_tags("inst-1", "project", "p1", ["b"])
        assert r.tags == {"a", "c"}

    def test_remove_nonexistent_tag(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["a"])
        r = m.remove_tags("inst-1", "project", "p1", ["z"])
        assert r.tags == {"a"}

    def test_remove_from_unknown_resource(self):
        m = AppTagManager()
        with pytest.raises(KeyError):
            m.remove_tags("inst-1", "x", "y", ["z"])


class TestGetTags:
    def test_get(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["x", "y"])
        assert m.get_tags("inst-1", "project", "p1") == {"x", "y"}

    def test_unknown_returns_empty(self):
        m = AppTagManager()
        assert m.get_tags("inst-1", "x", "y") == set()


class TestFindByTag:
    def test_find(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["env:prod"])
        m.add_tags("inst-1", "project", "p2", ["env:staging"])
        m.add_tags("inst-1", "project", "p3", ["env:prod"])
        results = m.find_by_tag("inst-1", "env:prod")
        assert len(results) == 2

    def test_filter_by_type(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["important"])
        m.add_tags("inst-1", "user", "u1", ["important"])
        results = m.find_by_tag("inst-1", "important", resource_type="project")
        assert len(results) == 1


class TestFindByPrefix:
    def test_prefix(self):
        m = AppTagManager()
        m.add_tags("inst-1", "project", "p1", ["env:prod", "team:backend"])
        m.add_tags("inst-1", "project", "p2", ["team:frontend"])
        results = m.find_by_prefix("inst-1", "env:")
        assert len(results) == 1


class TestAllTags:
    def test_all_tags(self):
        m = AppTagManager()
        m.add_tags("inst-1", "p", "1", ["a", "b"])
        m.add_tags("inst-1", "p", "2", ["b", "c"])
        assert m.all_tags("inst-1") == ["a", "b", "c"]


class TestTagCounts:
    def test_counts(self):
        m = AppTagManager()
        m.add_tags("inst-1", "p", "1", ["a", "b"])
        m.add_tags("inst-1", "p", "2", ["b", "c"])
        counts = m.tag_counts("inst-1")
        assert counts["a"] == 1
        assert counts["b"] == 2
        assert counts["c"] == 1


class TestIsolation:
    def test_cross_installation(self):
        m = AppTagManager()
        m.add_tags("inst-1", "p", "1", ["x"])
        assert m.get_tags("inst-2", "p", "1") == set()
        assert m.find_by_tag("inst-2", "x") == []
