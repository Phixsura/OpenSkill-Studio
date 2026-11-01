"""Tests for Config Schema Validator — type checks, constraints, defaults, sensitive masking."""

import pytest

from app.services.config_schema_validator import (
    ConfigSchemaValidator,
    FieldSchema,
    FieldType,
)


def _basic_schema() -> list[FieldSchema]:
    return [
        FieldSchema(name="api_key", field_type=FieldType.STRING, required=True, sensitive=True),
        FieldSchema(name="webhook_url", field_type=FieldType.URL, required=True),
        FieldSchema(name="max_retries", field_type=FieldType.INTEGER, required=False, default=3, min_value=0, max_value=10),
        FieldSchema(name="notify_email", field_type=FieldType.EMAIL, required=False),
        FieldSchema(name="enabled", field_type=FieldType.BOOLEAN, required=False, default=True),
        FieldSchema(name="mode", field_type=FieldType.ENUM, required=True, enum_values=["sync", "async", "batch"]),
    ]


class TestTypeValidation:
    def test_valid_config(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({
            "api_key": "sk-123456",
            "webhook_url": "https://example.com/hook",
            "mode": "sync",
        })
        assert result.valid is True
        assert result.errors == []

    def test_wrong_type_string(self):
        v = ConfigSchemaValidator([FieldSchema("name", FieldType.STRING)])
        result = v.validate({"name": 123})
        assert result.valid is False
        assert any("Expected string" in e.message for e in result.errors)

    def test_wrong_type_integer(self):
        v = ConfigSchemaValidator([FieldSchema("count", FieldType.INTEGER)])
        result = v.validate({"count": "not-a-number"})
        assert result.valid is False

    def test_boolean_not_integer(self):
        v = ConfigSchemaValidator([FieldSchema("count", FieldType.INTEGER)])
        result = v.validate({"count": True})
        assert result.valid is False

    def test_number_accepts_float(self):
        v = ConfigSchemaValidator([FieldSchema("rate", FieldType.NUMBER)])
        result = v.validate({"rate": 3.14})
        assert result.valid is True

    def test_number_accepts_int(self):
        v = ConfigSchemaValidator([FieldSchema("rate", FieldType.NUMBER)])
        result = v.validate({"rate": 42})
        assert result.valid is True

    def test_json_accepts_dict(self):
        v = ConfigSchemaValidator([FieldSchema("data", FieldType.JSON)])
        result = v.validate({"data": {"key": "value"}})
        assert result.valid is True

    def test_json_accepts_list(self):
        v = ConfigSchemaValidator([FieldSchema("data", FieldType.JSON)])
        result = v.validate({"data": [1, 2, 3]})
        assert result.valid is True


class TestRequiredAndDefaults:
    def test_missing_required_field(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({"mode": "sync", "webhook_url": "https://x.com/h"})
        assert result.valid is False
        assert any("api_key" in e.field for e in result.errors)

    def test_default_injected(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({
            "api_key": "sk-abc",
            "webhook_url": "https://x.com/h",
            "mode": "sync",
        })
        assert result.valid is True
        assert result.sanitized["max_retries"] == 3
        assert result.sanitized["enabled"] is True

    def test_apply_defaults(self):
        v = ConfigSchemaValidator(_basic_schema())
        filled = v.apply_defaults({"api_key": "sk-abc"})
        assert filled["max_retries"] == 3
        assert filled["enabled"] is True
        assert filled["api_key"] == "sk-abc"

    def test_optional_missing_no_error(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({
            "api_key": "sk-abc",
            "webhook_url": "https://x.com/h",
            "mode": "sync",
        })
        assert result.valid is True

    def test_unknown_fields_warning(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({
            "api_key": "sk-abc",
            "webhook_url": "https://x.com/h",
            "mode": "sync",
            "unknown_thing": "hello",
        })
        assert result.valid is True
        assert any("unknown_thing" in w.lower() for w in result.warnings)


class TestStringConstraints:
    def test_min_length(self):
        v = ConfigSchemaValidator([
            FieldSchema("code", FieldType.STRING, min_length=3),
        ])
        result = v.validate({"code": "ab"})
        assert result.valid is False
        assert any("3 characters" in e.message for e in result.errors)

    def test_max_length(self):
        v = ConfigSchemaValidator([
            FieldSchema("code", FieldType.STRING, max_length=5),
        ])
        result = v.validate({"code": "abcdef"})
        assert result.valid is False

    def test_pattern_match(self):
        v = ConfigSchemaValidator([
            FieldSchema("slug", FieldType.STRING, pattern=r"^[a-z0-9-]+$"),
        ])
        assert v.validate({"slug": "my-app-123"}).valid is True
        assert v.validate({"slug": "My App!"}).valid is False


class TestNumberConstraints:
    def test_min_value(self):
        v = ConfigSchemaValidator([
            FieldSchema("retries", FieldType.INTEGER, min_value=0),
        ])
        result = v.validate({"retries": -1})
        assert result.valid is False
        assert any(">=" in e.message for e in result.errors)

    def test_max_value(self):
        v = ConfigSchemaValidator([
            FieldSchema("retries", FieldType.INTEGER, max_value=10),
        ])
        result = v.validate({"retries": 15})
        assert result.valid is False

    def test_within_range(self):
        v = ConfigSchemaValidator([
            FieldSchema("retries", FieldType.INTEGER, min_value=0, max_value=10),
        ])
        assert v.validate({"retries": 5}).valid is True


class TestEnumValidation:
    def test_valid_enum(self):
        v = ConfigSchemaValidator([
            FieldSchema("mode", FieldType.ENUM, enum_values=["a", "b", "c"]),
        ])
        assert v.validate({"mode": "b"}).valid is True

    def test_invalid_enum(self):
        v = ConfigSchemaValidator([
            FieldSchema("mode", FieldType.ENUM, enum_values=["a", "b", "c"]),
        ])
        result = v.validate({"mode": "x"})
        assert result.valid is False
        assert any("one of" in e.message for e in result.errors)


class TestURLAndEmail:
    def test_valid_url(self):
        v = ConfigSchemaValidator([FieldSchema("url", FieldType.URL)])
        assert v.validate({"url": "https://example.com/path"}).valid is True

    def test_invalid_url(self):
        v = ConfigSchemaValidator([FieldSchema("url", FieldType.URL)])
        assert v.validate({"url": "not-a-url"}).valid is False

    def test_valid_email(self):
        v = ConfigSchemaValidator([FieldSchema("email", FieldType.EMAIL)])
        assert v.validate({"email": "user@example.com"}).valid is True

    def test_invalid_email(self):
        v = ConfigSchemaValidator([FieldSchema("email", FieldType.EMAIL)])
        assert v.validate({"email": "not-an-email"}).valid is False


class TestNestedObject:
    def test_nested_valid(self):
        v = ConfigSchemaValidator([
            FieldSchema("db", FieldType.OBJECT, properties={
                "host": FieldSchema("host", FieldType.STRING),
                "port": FieldSchema("port", FieldType.INTEGER, min_value=1, max_value=65535),
            }),
        ])
        result = v.validate({"db": {"host": "localhost", "port": 5432}})
        assert result.valid is True

    def test_nested_missing_required(self):
        v = ConfigSchemaValidator([
            FieldSchema("db", FieldType.OBJECT, properties={
                "host": FieldSchema("host", FieldType.STRING),
                "port": FieldSchema("port", FieldType.INTEGER),
            }),
        ])
        result = v.validate({"db": {"host": "localhost"}})
        assert result.valid is False
        assert any("db.port" in e.field for e in result.errors)

    def test_nested_wrong_type(self):
        v = ConfigSchemaValidator([
            FieldSchema("db", FieldType.OBJECT, properties={
                "port": FieldSchema("port", FieldType.INTEGER),
            }),
        ])
        result = v.validate({"db": {"port": "not-a-number"}})
        assert result.valid is False


class TestSensitiveMasking:
    def test_sensitive_masked_in_sanitized(self):
        v = ConfigSchemaValidator(_basic_schema())
        result = v.validate({
            "api_key": "sk-secret-key",
            "webhook_url": "https://x.com/h",
            "mode": "sync",
        })
        assert result.sanitized["api_key"] == "••••••••"
        assert result.sanitized["webhook_url"] == "https://x.com/h"

    def test_mask_sensitive(self):
        v = ConfigSchemaValidator(_basic_schema())
        masked = v.mask_sensitive({"api_key": "sk-secret", "mode": "sync"})
        assert masked["api_key"] == "••••••••"
        assert masked["mode"] == "sync"

    def test_sensitive_masked_in_errors(self):
        v = ConfigSchemaValidator([
            FieldSchema("secret", FieldType.STRING, sensitive=True, min_length=10),
        ])
        result = v.validate({"secret": "short"})
        assert result.valid is False
        assert result.errors[0].value == "••••••••"


class TestConfigDiff:
    def test_no_diff(self):
        v = ConfigSchemaValidator(_basic_schema())
        d = v.diff({"a": 1, "b": 2}, {"a": 1, "b": 2})
        assert d.added == []
        assert d.removed == []
        assert d.changed == []
        assert d.unchanged == ["a", "b"]

    def test_added_fields(self):
        v = ConfigSchemaValidator(_basic_schema())
        d = v.diff({"a": 1}, {"a": 1, "b": 2})
        assert d.added == ["b"]

    def test_removed_fields(self):
        v = ConfigSchemaValidator(_basic_schema())
        d = v.diff({"a": 1, "b": 2}, {"a": 1})
        assert d.removed == ["b"]

    def test_changed_fields(self):
        v = ConfigSchemaValidator(_basic_schema())
        d = v.diff({"a": 1, "b": "old"}, {"a": 1, "b": "new"})
        assert d.changed == ["b"]
        assert d.unchanged == ["a"]
