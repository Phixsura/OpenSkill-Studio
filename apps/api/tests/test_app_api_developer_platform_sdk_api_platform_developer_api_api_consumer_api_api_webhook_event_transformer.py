from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_webhook_event_transformer import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer, EventTransformConfig, EventTransformRule,
)

class TestWebhookEventTransformer:
    def test_rename(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer()
        svc.configure("inst-1", EventTransformConfig(consumer_id="c1", event_type="order.created", rules=[EventTransformRule(rule_id="r1", source_field="order_id", target_field="id", operation="rename")]))
        result = svc.transform("inst-1", "c1", "order.created", {"order_id": "o1", "total": 100})
        assert result["id"] == "o1" and "order_id" not in result

    def test_default_value(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer()
        svc.configure("inst-1", EventTransformConfig(consumer_id="c1", event_type="user.created", rules=[EventTransformRule(rule_id="r1", source_field="role", operation="default", default_value="member")]))
        result = svc.transform("inst-1", "c1", "user.created", {"name": "Alice"})
        assert result["role"] == "member"

    def test_value_map(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer()
        svc.configure("inst-1", EventTransformConfig(consumer_id="c1", event_type="order.updated", rules=[EventTransformRule(rule_id="r1", source_field="status", operation="map", value_map={"paid": "completed", "pending": "processing"})]))
        result = svc.transform("inst-1", "c1", "order.updated", {"status": "paid"})
        assert result["status"] == "completed"

    def test_disabled_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer()
        svc.configure("inst-1", EventTransformConfig(consumer_id="c1", event_type="x", enabled=False, rules=[EventTransformRule(rule_id="r1", source_field="x", operation="remove")]))
        result = svc.transform("inst-1", "c1", "x", {"x": "keep"})
        assert "x" in result

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiWebhookEventTransformer()
        svc.configure("inst-1", EventTransformConfig(consumer_id="c1", event_type="x"))
        assert len(svc.list_configs("inst-2")) == 0
