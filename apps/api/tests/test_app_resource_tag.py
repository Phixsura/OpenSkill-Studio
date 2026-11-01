"""Tests for App Resource Tag — tag, untag, query."""

import pytest

from app.services.app_resource_tag import AppResourceTag


class TestTag:
    def test_tag(self):
        t = AppResourceTag()
        r = t.tag("inst-1", "app-1", "app", ["production", "critical"])
        assert r.tags == {"production", "critical"}

    def test_normalize(self):
        t = AppResourceTag()
        r = t.tag("inst-1", "app-1", "app", ["  Production  ", "CRITICAL"])
        assert "production" in r.tags

    def test_append(self):
        t = AppResourceTag()
        t.tag("inst-1", "app-1", "app", ["production"])
        r = t.tag("inst-1", "app-1", "app", ["critical"])
        assert r.tags == {"production", "critical"}


class TestUntag:
    def test_untag(self):
        t = AppResourceTag()
        t.tag("inst-1", "app-1", "app", ["a", "b", "c"])
        r = t.untag("inst-1", "app-1", ["b"])
        assert r.tags == {"a", "c"}


class TestQuery:
    def test_find_by_tag(self):
        t = AppResourceTag()
        t.tag("inst-1", "app-1", "app", ["production"])
        t.tag("inst-1", "app-2", "app", ["staging"])
        t.tag("inst-1", "wh-1", "webhook", ["production"])
        results = t.find_by_tag("inst-1", "production")
        assert len(results) == 2

    def test_all_tags(self):
        t = AppResourceTag()
        t.tag("inst-1", "app-1", "app", ["production", "critical"])
        t.tag("inst-1", "app-2", "app", ["production"])
        tags = t.all_tags("inst-1")
        assert tags[0]["tag"] == "production"
        assert tags[0]["count"] == 2


class TestIsolation:
    def test_cross(self):
        t = AppResourceTag()
        t.tag("inst-1", "app-1", "app", ["production"])
        assert t.find_by_tag("inst-2", "production") == []
