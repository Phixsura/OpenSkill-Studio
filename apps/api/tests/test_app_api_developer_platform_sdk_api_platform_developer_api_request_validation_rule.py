import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_request_validation_rule import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule, ValidationRule,
)

class TestRequestValidationRule:
    def test_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule()
        svc.add_rule("inst-1", "/api", ValidationRule(rule_id="r1", field_name="name", rule_type="required"))
        errs = svc.validate("inst-1", "/api", {})
        assert len(errs) == 1
        assert errs[0].field == "name"

    def test_regex(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule()
        svc.add_rule("inst-1", "/api", ValidationRule(rule_id="r1", field_name="email", rule_type="regex", config={"pattern": r"^[\w.]+@[\w.]+$"}))
        assert len(svc.validate("inst-1", "/api", {"email": "a@b.com"})) == 0
        assert len(svc.validate("inst-1", "/api", {"email": "bad"})) == 1

    def test_enum(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule()
        svc.add_rule("inst-1", "/api", ValidationRule(rule_id="r1", field_name="status", rule_type="enum", config={"values": ["active", "inactive"]}))
        assert len(svc.validate("inst-1", "/api", {"status": "active"})) == 0
        assert len(svc.validate("inst-1", "/api", {"status": "deleted"})) == 1

    def test_bool_guard_on_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule()
        svc.add_rule("inst-1", "/api", ValidationRule(rule_id="r1", field_name="count", rule_type="type", config={"expected": "int"}))
        assert len(svc.validate("inst-1", "/api", {"count": True})) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiRequestValidationRule()
        svc.add_rule("inst-1", "/api", ValidationRule(rule_id="r1", field_name="x", rule_type="required"))
        assert svc.rule_count("inst-2") == 0
