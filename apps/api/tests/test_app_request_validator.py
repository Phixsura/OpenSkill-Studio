"""Tests for App Request Validator — types, ranges, lengths, required."""

import pytest

from app.services.app_request_validator import AppRequestValidator, FieldRule


@pytest.fixture
def validator():
    v = AppRequestValidator()
    v.define_schema("inst-1", "create_user", [
        FieldRule(field="name", required=True, field_type="string", min_length=1, max_length=100),
        FieldRule(field="email", required=True, field_type="string"),
        FieldRule(field="age", required=False, field_type="int", min_value=0, max_value=150),
        FieldRule(field="active", required=False, field_type="bool"),
        FieldRule(field="tags", required=False, field_type="list"),
    ])
    return v


class TestValid:
    def test_valid_payload(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "Alice", "email": "alice@example.com", "age": 30,
        })
        assert r.valid is True
        assert r.issues == []


class TestRequired:
    def test_missing_required(self, validator):
        r = validator.validate("inst-1", "create_user", {"email": "a@b.com"})
        assert r.valid is False
        assert any(i.field == "name" for i in r.issues)

    def test_optional_missing_ok(self, validator):
        r = validator.validate("inst-1", "create_user", {"name": "A", "email": "a@b.com"})
        assert r.valid is True


class TestTypes:
    def test_wrong_type(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": 123, "email": "a@b.com",
        })
        assert any(i.field == "name" and "string" in i.message for i in r.issues)

    def test_bool_not_int(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "A", "email": "a@b.com", "age": True,
        })
        assert any(i.field == "age" for i in r.issues)


class TestLength:
    def test_too_short(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "", "email": "a@b.com",
        })
        assert any("short" in i.message for i in r.issues)

    def test_too_long(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "x" * 101, "email": "a@b.com",
        })
        assert any("long" in i.message for i in r.issues)


class TestRange:
    def test_below_min(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "A", "email": "a@b.com", "age": -1,
        })
        assert any("minimum" in i.message for i in r.issues)

    def test_above_max(self, validator):
        r = validator.validate("inst-1", "create_user", {
            "name": "A", "email": "a@b.com", "age": 200,
        })
        assert any("maximum" in i.message for i in r.issues)


class TestSchema:
    def test_unknown_schema(self, validator):
        with pytest.raises(KeyError):
            validator.validate("inst-1", "nope", {})

    def test_list_schemas(self, validator):
        assert "create_user" in validator.list_schemas("inst-1")


class TestIsolation:
    def test_cross_installation(self, validator):
        with pytest.raises(KeyError):
            validator.validate("inst-2", "create_user", {})
