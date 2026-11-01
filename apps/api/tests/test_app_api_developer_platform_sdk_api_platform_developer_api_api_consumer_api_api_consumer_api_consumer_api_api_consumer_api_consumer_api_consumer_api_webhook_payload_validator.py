import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_consumer_api_consumer_api_webhook_payload_validator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator, PayloadSchema, PayloadRule,
)

class TestWebhookPayloadValidator:
    def test_valid_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        svc.register_schema("inst-1", PayloadSchema(schema_id="s1", event_type="order.created", rules=[
            PayloadRule(field_path="order_id", rule_type="required"),
            PayloadRule(field_path="order_id", rule_type="type", value="string"),
        ]))
        result = svc.validate("inst-1", "order.created", {"order_id": "O123", "total": 99.99})
        assert result.valid

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        svc.register_schema("inst-1", PayloadSchema(schema_id="s1", event_type="e", rules=[PayloadRule(field_path="id", rule_type="required")]))
        result = svc.validate("inst-1", "e", {})
        assert not result.valid and "required" in result.errors[0]

    def test_wrong_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        svc.register_schema("inst-1", PayloadSchema(schema_id="s1", event_type="e", rules=[PayloadRule(field_path="count", rule_type="type", value="integer")]))
        assert not svc.validate("inst-1", "e", {"count": "five"}).valid

    def test_bool_not_int(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        svc.register_schema("inst-1", PayloadSchema(schema_id="s1", event_type="e", rules=[PayloadRule(field_path="n", rule_type="type", value="integer")]))
        assert not svc.validate("inst-1", "e", {"n": True}).valid

    def test_oversized_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator(max_payload_bytes=50)
        result = svc.validate("inst-1", "e", {"data": "x" * 100})
        assert not result.valid and "max size" in result.errors[0]

    def test_no_schema_passes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        assert svc.validate("inst-1", "unknown", {"any": "thing"}).valid

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiConsumerApiConsumerApiWebhookPayloadValidator()
        svc.register_schema("inst-1", PayloadSchema(schema_id="s1", event_type="e", rules=[PayloadRule(field_path="x", rule_type="required")]))
        assert svc.validate("inst-2", "e", {}).valid  # no schema for inst-2
