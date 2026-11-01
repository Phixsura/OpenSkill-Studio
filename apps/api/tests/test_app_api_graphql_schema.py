"""Tests for App API GraphQL Schema — types, operations, stats."""

import pytest
from app.services.app_api_graphql_schema import AppAPIGraphQLSchema


class TestType:
    def test_register(self):
        g = AppAPIGraphQLSchema()
        t = g.register_type("inst-1", "User", "type", ["id", "name", "email"])
        assert len(t.fields) == 3

    def test_invalid_kind(self):
        g = AppAPIGraphQLSchema()
        with pytest.raises(ValueError):
            g.register_type("inst-1", "Bad", "struct", [])


class TestOperation:
    def test_register(self):
        g = AppAPIGraphQLSchema()
        op = g.register_operation("inst-1", "getUser", "query", "User")
        assert op.operation_type == "query"


class TestStats:
    def test_stats(self):
        g = AppAPIGraphQLSchema()
        g.register_type("inst-1", "User", "type", ["id", "name"])
        g.register_type("inst-1", "Post", "type", ["id", "title", "body"])
        g.register_operation("inst-1", "getUser", "query", "User")
        g.register_operation("inst-1", "createUser", "mutation", "User")
        stats = g.schema_stats("inst-1")
        assert stats["types"] == 2
        assert stats["fields"] == 5
        assert stats["queries"] == 1
        assert stats["mutations"] == 1


class TestIsolation:
    def test_cross(self):
        g = AppAPIGraphQLSchema()
        g.register_type("inst-1", "User", "type", ["id"])
        assert g.list_types("inst-2") == []
