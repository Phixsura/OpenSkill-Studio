"""Tests for App API Request Transform — headers, query, path."""

import pytest
from app.services.app_api_request_transform import AppAPIRequestTransform


class TestRules:
    def test_add_header(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "add_header", "X-Tenant", "acme")
        result = t.apply("inst-1", {}, {}, "/api")
        assert result["headers"]["X-Tenant"] == "acme"

    def test_remove_header(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "remove_header", "X-Debug")
        result = t.apply("inst-1", {"X-Debug": "true", "Accept": "json"}, {}, "/api")
        assert "X-Debug" not in result["headers"]
        assert "Accept" in result["headers"]

    def test_add_query(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "add_query", "format", "json")
        result = t.apply("inst-1", {}, {}, "/api")
        assert result["query"]["format"] == "json"

    def test_add_query_no_overwrite(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "add_query", "format", "json")
        result = t.apply("inst-1", {}, {"format": "xml"}, "/api")
        assert result["query"]["format"] == "xml"

    def test_rewrite_path(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "rewrite_path", "/v1/", "/v2/")
        result = t.apply("inst-1", {}, {}, "/v1/users")
        assert result["path"] == "/v2/users"


class TestIsolation:
    def test_cross(self):
        t = AppAPIRequestTransform()
        t.add_rule("inst-1", "r1", "add_header", "X", "Y")
        result = t.apply("inst-2", {}, {}, "/api")
        assert "X" not in result["headers"]
