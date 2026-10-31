"""Tests for App API Endpoint Tag — tag, find, all_tags."""

from app.services.app_api_endpoint_tag import AppAPIEndpointTag


class TestTag:
    def test_tag(self):
        t = AppAPIEndpointTag()
        ep = t.tag("inst-1", "GET", "/api/users", ["public", "v2"])
        assert ep.tags == {"public", "v2"}

    def test_append(self):
        t = AppAPIEndpointTag()
        t.tag("inst-1", "GET", "/api/users", ["public"])
        ep = t.tag("inst-1", "GET", "/api/users", ["v2"])
        assert ep.tags == {"public", "v2"}


class TestFind:
    def test_by_tag(self):
        t = AppAPIEndpointTag()
        t.tag("inst-1", "GET", "/api/users", ["public"])
        t.tag("inst-1", "POST", "/api/apps", ["internal"])
        assert len(t.find_by_tag("inst-1", "public")) == 1

    def test_all_tags(self):
        t = AppAPIEndpointTag()
        t.tag("inst-1", "GET", "/a", ["public"])
        t.tag("inst-1", "GET", "/b", ["public", "v2"])
        tags = t.all_tags("inst-1")
        assert tags[0]["tag"] == "public"
        assert tags[0]["count"] == 2


class TestIsolation:
    def test_cross(self):
        t = AppAPIEndpointTag()
        t.tag("inst-1", "GET", "/api", ["public"])
        assert t.list_endpoints("inst-2") == []
