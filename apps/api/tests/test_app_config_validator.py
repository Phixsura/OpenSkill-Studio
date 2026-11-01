"""Tests for App Config Validator — type checking, constraints, defaults."""

import pytest

from app.services.app_config_validator import (
    AppConfigValidator,
    FieldSchema,
    FieldType,
)


@pytest.fixture
def validator():
    v = AppConfigValidator()
    v.register_schema("basic", [
        FieldSchema(name="name", field_type=FieldType.STRING, required=True),
        FieldSchema(name="port", field_type=FieldType.INT, required=True, min_value=1, max_value=65535),
        FieldSchema(name="debug", field_type=FieldType.BOOL, required=False),
        FieldSchema(name="rate", field_type=FieldType.FLOAT, min_value=0.0),
        FieldSchema(name="env", field_type=FieldType.ENUM, enum_values=["dev", "staging", "prod"]),
        FieldSchema(name="callback_url", field_type=FieldType.URL),
        FieldSchema(name="contact", field_type=FieldType.EMAIL),
    ])
    return v


class TestValidConfig:
    def test_valid(self, validator):
        r = validator.validate("basic", {
            "name": "my-app",
            "port": 8080,
            "rate": 1.5,
            "env": "prod",
            "callback_url": "https://example.com/hook",
            "contact": "admin@example.com",
        })
        assert r.valid is True
        assert len(r.errors) == 0

    def test_resolved_config_contains_values(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 3000,
            "rate": 0.5,
            "env": "dev",
            "callback_url": "https://x.com/h",
            "contact": "a@b.com",
        })
        assert r.resolved_config["name"] == "app"
        assert r.resolved_config["port"] == 3000


class TestRequired:
    def test_missing_required(self, validator):
        r = validator.validate("basic", {
            "port": 8080,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert r.valid is False
        assert any(e.field == "name" for e in r.errors)

    def test_optional_missing_ok(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 80,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        # debug is optional, no error
        assert not any(e.field == "debug" for e in r.errors)

    def test_default_value(self):
        v = AppConfigValidator()
        v.register_schema("with-default", [
            FieldSchema(name="timeout", field_type=FieldType.INT, required=True, default=30),
        ])
        r = v.validate("with-default", {})
        assert r.valid is True
        assert r.resolved_config["timeout"] == 30
        assert any("default" in w for w in r.warnings)


class TestTypeCheck:
    def test_wrong_type_string(self, validator):
        r = validator.validate("basic", {
            "name": 123,
            "port": 80,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert r.valid is False
        assert any(e.field == "name" and "string" in e.message for e in r.errors)

    def test_wrong_type_int(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": "eighty",
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert any(e.field == "port" for e in r.errors)

    def test_bool_not_treated_as_int(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": True,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert any(e.field == "port" for e in r.errors)


class TestRange:
    def test_below_min(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 0,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert any(e.field == "port" and "minimum" in e.message for e in r.errors)

    def test_above_max(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 99999,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert any(e.field == "port" and "maximum" in e.message for e in r.errors)


class TestEnum:
    def test_invalid_enum(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 80,
            "rate": 1.0,
            "env": "test",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
        })
        assert any(e.field == "env" for e in r.errors)


class TestFormat:
    def test_invalid_url(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 80,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "not-a-url",
            "contact": "a@b.com",
        })
        assert any(e.field == "callback_url" and "URL" in e.message for e in r.errors)

    def test_invalid_email(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 80,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "not-email",
        })
        assert any(e.field == "contact" and "email" in e.message for e in r.errors)


class TestPattern:
    def test_pattern_match(self):
        v = AppConfigValidator()
        v.register_schema("pat", [
            FieldSchema(name="slug", field_type=FieldType.STRING, pattern=r"^[a-z0-9-]+$"),
        ])
        r = v.validate("pat", {"slug": "my-app-123"})
        assert r.valid is True

    def test_pattern_mismatch(self):
        v = AppConfigValidator()
        v.register_schema("pat", [
            FieldSchema(name="slug", field_type=FieldType.STRING, pattern=r"^[a-z0-9-]+$"),
        ])
        r = v.validate("pat", {"slug": "My App!"})
        assert r.valid is False
        assert any("pattern" in e.message for e in r.errors)


class TestUnknownFields:
    def test_warns_on_unknown(self, validator):
        r = validator.validate("basic", {
            "name": "app",
            "port": 80,
            "rate": 1.0,
            "env": "dev",
            "callback_url": "https://x.com",
            "contact": "a@b.com",
            "extra_field": "wat",
        })
        assert any("Unknown" in w for w in r.warnings)


class TestSchemaManagement:
    def test_list_schemas(self, validator):
        assert "basic" in validator.list_schemas()

    def test_get_schema(self, validator):
        fields = validator.get_schema("basic")
        assert len(fields) == 7

    def test_unknown_schema(self):
        v = AppConfigValidator()
        with pytest.raises(KeyError):
            v.validate("nope", {})

    def test_empty_schema_id(self):
        v = AppConfigValidator()
        with pytest.raises(ValueError):
            v.register_schema("", [])
