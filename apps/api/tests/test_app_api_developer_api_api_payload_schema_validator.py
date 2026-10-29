import pytest
from app.services.app_api_developer_api_api_payload_schema_validator import AppAPIDeveloperAPIApiPayloadSchemaValidator

class TestPayloadSchemaValidator:
    def test_valid(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "user", [{"name": "email", "type": "email"}, {"name": "age", "type": "int"}])
        r = v.validate("inst-1", "user", {"email": "a@b.com", "age": 25})
        assert r.valid is True

    def test_missing_required(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "user", [{"name": "name", "type": "string"}])
        r = v.validate("inst-1", "user", {})
        assert r.valid is False
        assert any("Missing" in e for e in r.errors)

    def test_wrong_type(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "user", [{"name": "age", "type": "int"}])
        r = v.validate("inst-1", "user", {"age": "not_int"})
        assert r.valid is False

    def test_email_validation(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "s", [{"name": "email", "type": "email"}])
        assert v.validate("inst-1", "s", {"email": "valid@test.com"}).valid is True
        assert v.validate("inst-1", "s", {"email": "invalid"}).valid is False

    def test_bool_not_int(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "s", [{"name": "count", "type": "int"}])
        r = v.validate("inst-1", "s", {"count": True})
        assert r.valid is False

    def test_isolation(self):
        v = AppAPIDeveloperAPIApiPayloadSchemaValidator()
        v.register("inst-1", "s", [{"name": "x", "type": "string"}])
        with pytest.raises(KeyError):
            v.validate("inst-2", "s", {"x": "y"})
