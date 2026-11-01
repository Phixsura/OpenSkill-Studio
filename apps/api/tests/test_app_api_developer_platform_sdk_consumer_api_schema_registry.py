"""Tests for Consumer API Schema Registry service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_schema_registry import (
    SchemaRegistry, Schema, SchemaField,
)


class TestSchemaRegistry:
    def test_register_and_get(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int"), SchemaField("name", "string")]))
        schema = svc.get_schema("s1")
        assert schema is not None
        assert len(schema["fields"]) == 2

    def test_validate_valid(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int"), SchemaField("name", "string")]))
        result = svc.validate("s1", {"id": 1, "name": "Alice"})
        assert result["valid"] is True

    def test_validate_missing_required(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int"), SchemaField("email", "string")]))
        result = svc.validate("s1", {"id": 1})
        assert result["valid"] is False

    def test_validate_type_mismatch(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("count", "int")]))
        result = svc.validate("s1", {"count": "not_int"})
        assert result["valid"] is False

    def test_bool_as_int_guard(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("count", "int")]))
        result = svc.validate("s1", {"count": True})
        assert result["valid"] is False

    def test_compatibility_compatible(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))
        svc.register(Schema("s2", "ep1", "2.0", [SchemaField("id", "int"), SchemaField("email", "string")]))
        result = svc.check_compatibility("s1", "s2")
        assert result["compatible"] is True
        assert "email" in result["added"]

    def test_compatibility_breaking(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int"), SchemaField("name", "string")]))
        svc.register(Schema("s2", "ep1", "2.0", [SchemaField("id", "int")]))
        result = svc.check_compatibility("s1", "s2")
        assert result["compatible"] is False

    def test_get_versions(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))
        svc.register(Schema("s2", "ep1", "2.0", [SchemaField("id", "int"), SchemaField("name", "string")]))
        versions = svc.get_versions("ep1")
        assert versions[0]["version"] == "2.0"

    def test_get_latest(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))
        svc.register(Schema("s2", "ep1", "2.0", [SchemaField("id", "int")]))
        latest = svc.get_latest("ep1")
        assert latest["version"] == "2.0"

    def test_empty_fields(self):
        svc = SchemaRegistry()
        with pytest.raises(ValueError):
            svc.register(Schema("s1", "ep1", "1.0", []))

    def test_duplicate(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))
        with pytest.raises(ValueError):
            svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))

    def test_stats(self):
        svc = SchemaRegistry()
        svc.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")], direction="request"))
        svc.register(Schema("s2", "ep1", "1.0", [SchemaField("id", "int")], direction="response"))
        stats = svc.get_stats()
        assert stats["total_schemas"] == 2
        assert stats["request_schemas"] == 1

    def test_isolation(self):
        a, b = SchemaRegistry(), SchemaRegistry()
        a.register(Schema("s1", "ep1", "1.0", [SchemaField("id", "int")]))
        assert b.get_schema("s1") is None
