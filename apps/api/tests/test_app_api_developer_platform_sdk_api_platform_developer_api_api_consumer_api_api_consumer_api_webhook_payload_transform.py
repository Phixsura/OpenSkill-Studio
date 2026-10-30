import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_payload_transform import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform, TransformConfig, TransformRule,
)

class TestWebhookPayloadTransform:
    def test_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform()
        payload = {"event": "created", "data": {"id": "123"}}
        result = svc.transform("inst-1", "missing", payload)
        assert result == payload

    def test_rename_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform()
        cfg = TransformConfig(config_id="c1", webhook_id="wh1", rules=[
            TransformRule(rule_id="r1", source_path="data.user.email", target_path="contact.email"),
        ])
        svc.set_config("inst-1", cfg)
        result = svc.transform("inst-1", "c1", {"data": {"user": {"email": "a@b.com"}}})
        assert result["contact"]["email"] == "a@b.com"

    def test_drop_unmapped(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform()
        cfg = TransformConfig(config_id="c1", webhook_id="wh1", drop_unmapped=True, rules=[
            TransformRule(rule_id="r1", source_path="a", target_path="x"),
        ])
        svc.set_config("inst-1", cfg)
        result = svc.transform("inst-1", "c1", {"a": 1, "b": 2})
        assert result == {"x": 1}

    def test_default_value(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform()
        cfg = TransformConfig(config_id="c1", webhook_id="wh1", rules=[
            TransformRule(rule_id="r1", source_path="missing", target_path="out", default="fallback"),
        ])
        svc.set_config("inst-1", cfg)
        result = svc.transform("inst-1", "c1", {"other": "val"})
        assert result["out"] == "fallback"

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookPayloadTransform()
        cfg = TransformConfig(config_id="c1", webhook_id="wh1", rules=[])
        svc.set_config("inst-1", cfg)
        assert len(svc.list_configs("inst-2")) == 0
