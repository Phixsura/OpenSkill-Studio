from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_webhook_payload_validator import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator

class TestWebhookPayloadValidator:
    def test_valid_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator()
        r = svc.validate("inst-1", '{"event":"test","data":{"id":"1"}}')
        assert r.valid is True and len(r.errors) == 0

    def test_invalid_json(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator()
        r = svc.validate("inst-1", "not json")
        assert r.valid is False and "Invalid JSON" in r.errors[0]

    def test_too_large(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator(max_payload_bytes=1024)
        r = svc.validate("inst-1", json.dumps({"x": "a" * 2000}))
        assert r.valid is False

    def test_non_object(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator()
        r = svc.validate("inst-1", "[1,2,3]")
        assert r.valid is False

    def test_validation_rate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookPayloadValidator()
        svc.validate("inst-1", '{"ok":true}')
        svc.validate("inst-1", "bad")
        assert svc.validation_rate("inst-1") == 50.0

import json
