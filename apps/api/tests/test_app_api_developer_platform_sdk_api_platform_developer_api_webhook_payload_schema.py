import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_payload_schema import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema, PayloadSchema, SchemaField,
)

class TestWebhookPayloadSchema:
    def _make_schema(self):
        return PayloadSchema(schema_id="s1", event_type="order.created", version="1.0", fields=[
            SchemaField(name="order_id", field_type="string"),
            SchemaField(name="amount", field_type="int"),
            SchemaField(name="notes", field_type="string", required=False),
        ])

    def test_valid_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema()
        svc.register("inst-1", self._make_schema())
        violations = svc.validate("inst-1", "order.created", "1.0", {"order_id": "o1", "amount": 100})
        assert len(violations) == 0

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema()
        svc.register("inst-1", self._make_schema())
        violations = svc.validate("inst-1", "order.created", "1.0", {"amount": 100})
        assert len(violations) == 1 and violations[0].field == "order_id"

    def test_wrong_type(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema()
        svc.register("inst-1", self._make_schema())
        violations = svc.validate("inst-1", "order.created", "1.0", {"order_id": "o1", "amount": "not_int"})
        assert len(violations) == 1 and violations[0].field == "amount"

    def test_bool_guard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema()
        svc.register("inst-1", self._make_schema())
        violations = svc.validate("inst-1", "order.created", "1.0", {"order_id": "o1", "amount": True})
        assert len(violations) == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookPayloadSchema()
        svc.register("inst-1", self._make_schema())
        assert len(svc.list_schemas("inst-2")) == 0
