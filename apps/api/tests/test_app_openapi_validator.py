"""Tests for App OpenAPI Validator — schemas, validation, compliance."""

import pytest

from app.services.app_openapi_validator import AppOpenAPIValidator


@pytest.fixture
def validator():
    v = AppOpenAPIValidator()
    v.register_schema("inst-1", "GET", "/api/users",
                       response_fields={"id": "string", "name": "string", "age": "int", "active": "bool"},
                       required_fields=["id", "name"])
    return v


class TestRegister:
    def test_register(self, validator):
        schemas = validator.list_schemas("inst-1")
        assert len(schemas) == 1

    def test_missing_method(self):
        v = AppOpenAPIValidator()
        with pytest.raises(ValueError):
            v.register_schema("inst-1", "", "/api", {})


class TestValidate:
    def test_valid(self, validator):
        r = validator.validate_response("inst-1", "GET", "/api/users",
                                         {"id": "u1", "name": "Alice", "age": 30, "active": True})
        assert r.valid is True

    def test_missing_required(self, validator):
        r = validator.validate_response("inst-1", "GET", "/api/users",
                                         {"id": "u1"})
        assert r.valid is False
        assert any(v.field == "name" for v in r.violations)

    def test_wrong_type(self, validator):
        r = validator.validate_response("inst-1", "GET", "/api/users",
                                         {"id": "u1", "name": "Alice", "age": "thirty"})
        assert any(v.field == "age" for v in r.violations)

    def test_bool_not_int(self, validator):
        r = validator.validate_response("inst-1", "GET", "/api/users",
                                         {"id": "u1", "name": "Alice", "age": True})
        assert any(v.field == "age" for v in r.violations)

    def test_unknown_schema(self, validator):
        with pytest.raises(KeyError):
            validator.validate_response("inst-1", "POST", "/api/nope", {})


class TestCompliance:
    def test_rate(self, validator):
        validator.validate_response("inst-1", "GET", "/api/users", {"id": "u1", "name": "A"})
        validator.validate_response("inst-1", "GET", "/api/users", {"id": "u1"})  # fails
        assert validator.compliance_rate("inst-1", "GET", "/api/users") == 50.0

    def test_no_checks(self, validator):
        assert validator.compliance_rate("inst-1", "GET", "/api/users") == 100.0


class TestIsolation:
    def test_cross_installation(self, validator):
        with pytest.raises(KeyError):
            validator.validate_response("inst-2", "GET", "/api/users", {})
