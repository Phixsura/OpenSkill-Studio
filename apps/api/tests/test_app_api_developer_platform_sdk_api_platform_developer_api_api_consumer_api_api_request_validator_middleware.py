import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_request_validator_middleware import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware, ValidationMiddlewareRule,
)

class TestRequestValidatorMiddleware:
    def test_required_field(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware()
        svc.add_rule("inst-1", "/api/users", ValidationMiddlewareRule(rule_id="r1", target="header", field_name="Authorization", check="required"))
        r = svc.validate_request("inst-1", "/api/users", headers={})
        assert r.valid is False
        r2 = svc.validate_request("inst-1", "/api/users", headers={"Authorization": "Bearer x"})
        assert r2.valid is True

    def test_regex_validation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware()
        svc.add_rule("inst-1", "/api", ValidationMiddlewareRule(rule_id="r1", target="query", field_name="email", check="regex", config={"pattern": r"^[\w.]+@[\w.]+$"}))
        assert svc.validate_request("inst-1", "/api", query={"email": "a@b.com"}).valid is True
        assert svc.validate_request("inst-1", "/api", query={"email": "bad"}).valid is False

    def test_max_length(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware()
        svc.add_rule("inst-1", "/api", ValidationMiddlewareRule(rule_id="r1", target="body", field_name="name", check="max_length", config={"max": "50"}))
        assert svc.validate_request("inst-1", "/api", body={"name": "x" * 100}).valid is False

    def test_rejection_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware()
        svc.add_rule("inst-1", "/api", ValidationMiddlewareRule(rule_id="r1", target="header", field_name="X-Key", check="required"))
        svc.validate_request("inst-1", "/api", headers={"X-Key": "v"})
        svc.validate_request("inst-1", "/api", headers={})
        assert svc.rejection_rate("inst-1") == 50.0

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiRequestValidatorMiddleware()
        svc.add_rule("inst-1", "/api", ValidationMiddlewareRule(rule_id="r1", target="header", field_name="X", check="required"))
        assert svc.rule_count("inst-2") == 0
