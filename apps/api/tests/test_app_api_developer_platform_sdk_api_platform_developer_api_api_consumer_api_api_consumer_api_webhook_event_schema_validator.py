import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_event_schema_validator import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator, EventSchema, SchemaField,
)

class TestWebhookEventSchemaValidator:
    def test_valid_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        schema = EventSchema(schema_id="s1", event_type="order.created", version="1.0", fields=[
            SchemaField(name="order_id", field_type="string"), SchemaField(name="amount", field_type="integer"),
        ])
        svc.register("inst-1", schema)
        result = svc.validate("inst-1", "s1", {"order_id": "o123", "amount": 100})
        assert result.valid

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        svc.register("inst-1", EventSchema(schema_id="s1", event_type="e", version="1", fields=[SchemaField(name="id", field_type="string")]))
        result = svc.validate("inst-1", "s1", {})
        assert not result.valid and result.errors[0].message == "required field missing"

    def test_wrong_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        svc.register("inst-1", EventSchema(schema_id="s1", event_type="e", version="1", fields=[SchemaField(name="count", field_type="integer")]))
        result = svc.validate("inst-1", "s1", {"count": "not_a_number"})
        assert not result.valid and "expected integer" in result.errors[0].message

    def test_bool_not_int(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        svc.register("inst-1", EventSchema(schema_id="s1", event_type="e", version="1", fields=[SchemaField(name="n", field_type="integer")]))
        result = svc.validate("inst-1", "s1", {"n": True})
        assert not result.valid

    def test_string_length(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        svc.register("inst-1", EventSchema(schema_id="s1", event_type="e", version="1", fields=[SchemaField(name="code", field_type="string", min_length=3, max_length=10)]))
        assert svc.validate("inst-1", "s1", {"code": "AB"}).valid is False
        assert svc.validate("inst-1", "s1", {"code": "ABC"}).valid is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookEventSchemaValidator()
        svc.register("inst-1", EventSchema(schema_id="s1", event_type="e", version="1", fields=[]))
        assert svc.get_schema("inst-2", "s1") is None
