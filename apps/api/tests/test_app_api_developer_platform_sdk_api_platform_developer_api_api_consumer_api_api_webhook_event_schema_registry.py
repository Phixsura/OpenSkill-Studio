from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_schema_registry import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry, EventSchema,
)

class TestWebhookEventSchemaRegistry:
    def test_validate_valid(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry()
        svc.register("inst-1", EventSchema(event_type="order.created", version="v1", required_fields=["order_id"], fields={"order_id": "string", "total": "int"}))
        r = svc.validate_event("inst-1", "order.created", "v1", {"order_id": "o1", "total": 100})
        assert r.valid is True

    def test_missing_required(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry()
        svc.register("inst-1", EventSchema(event_type="order.created", version="v1", required_fields=["order_id"]))
        r = svc.validate_event("inst-1", "order.created", "v1", {"total": 100})
        assert r.valid is False

    def test_bool_guard(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry()
        svc.register("inst-1", EventSchema(event_type="x", version="v1", fields={"count": "int"}))
        r = svc.validate_event("inst-1", "x", "v1", {"count": True})
        assert r.valid is False

    def test_no_schema_passes(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry()
        assert svc.validate_event("inst-1", "unknown", "v1", {}).valid is True

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventSchemaRegistry()
        svc.register("inst-1", EventSchema(event_type="x", version="v1"))
        assert len(svc.list_schemas("inst-2")) == 0
