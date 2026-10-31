import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_request_validator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator, EndpointValidation, ValidationRule,
)

class TestConsumerApiRequestValidator:
    def test_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        svc.register("inst-1", EndpointValidation(endpoint_path="/api/orders", method="POST", rules=[ValidationRule(field_path="item_id", rule_type="required")]))
        result = svc.validate("inst-1", "/api/orders", "POST", {})
        assert not result.valid and result.errors[0].rule == "required"

    def test_type_check(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        svc.register("inst-1", EndpointValidation(endpoint_path="/api", method="POST", rules=[ValidationRule(field_path="count", rule_type="type", value="integer")]))
        assert not svc.validate("inst-1", "/api", "POST", {"count": "not_int"}).valid
        assert svc.validate("inst-1", "/api", "POST", {"count": 5}).valid

    def test_bool_not_int(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        svc.register("inst-1", EndpointValidation(endpoint_path="/api", method="POST", rules=[ValidationRule(field_path="n", rule_type="type", value="integer")]))
        assert not svc.validate("inst-1", "/api", "POST", {"n": True}).valid

    def test_min_max(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        svc.register("inst-1", EndpointValidation(endpoint_path="/api", method="POST", rules=[ValidationRule(field_path="qty", rule_type="min", value="1"), ValidationRule(field_path="qty", rule_type="max", value="100")]))
        assert not svc.validate("inst-1", "/api", "POST", {"qty": 0}).valid
        assert svc.validate("inst-1", "/api", "POST", {"qty": 50}).valid

    def test_enum(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        svc.register("inst-1", EndpointValidation(endpoint_path="/api", method="POST", rules=[ValidationRule(field_path="status", rule_type="enum", value="active,inactive")]))
        assert svc.validate("inst-1", "/api", "POST", {"status": "active"}).valid
        assert not svc.validate("inst-1", "/api", "POST", {"status": "deleted"}).valid

    def test_no_validation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRequestValidator()
        assert svc.validate("inst-1", "/api", "GET", {}).valid
