import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_request_validator_v2 import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2, ValidationSchema, ValidationRule,
)

class TestEndpointRequestValidatorV2:
    def test_nested_field(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api/orders", method="POST", rules=[
            ValidationRule(field_path="data.user.email", rule_type="required"),
        ]))
        assert svc.validate("inst-1", "/api/orders", "POST", {"data": {"user": {"email": "a@b.com"}}}).valid
        assert not svc.validate("inst-1", "/api/orders", "POST", {"data": {"user": {}}}).valid

    def test_pattern(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[
            ValidationRule(field_path="email", rule_type="pattern", value=r"^[^@]+@[^@]+\.[^@]+$"),
        ]))
        assert svc.validate("inst-1", "/api", "POST", {"email": "test@example.com"}).valid
        assert not svc.validate("inst-1", "/api", "POST", {"email": "not-an-email"}).valid

    def test_range(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[
            ValidationRule(field_path="quantity", rule_type="range", value="1,100"),
        ]))
        assert svc.validate("inst-1", "/api", "POST", {"quantity": 50}).valid
        assert not svc.validate("inst-1", "/api", "POST", {"quantity": 200}).valid

    def test_bool_not_int(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[
            ValidationRule(field_path="count", rule_type="type", value="integer"),
        ]))
        assert not svc.validate("inst-1", "/api", "POST", {"count": True}).valid

    def test_custom_message(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[
            ValidationRule(field_path="name", rule_type="required", message="Name is mandatory"),
        ]))
        result = svc.validate("inst-1", "/api", "POST", {})
        assert result.errors[0] == "Name is mandatory"

    def test_invalid_rule_type(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        with pytest.raises(ValueError, match="Unknown rule_type"):
            svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[
                ValidationRule(field_path="x", rule_type="unknown"),
            ]))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointRequestValidatorV2()
        svc.register("inst-1", ValidationSchema(schema_id="s1", endpoint_path="/api", method="POST", rules=[ValidationRule(field_path="x", rule_type="required")]))
        assert svc.validate("inst-2", "/api", "POST", {}).valid
