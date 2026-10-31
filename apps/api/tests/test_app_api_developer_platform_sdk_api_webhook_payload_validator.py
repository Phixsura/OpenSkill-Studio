from app.services.app_api_developer_platform_sdk_api_webhook_payload_validator import AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator

class TestWebhookPayloadValidator:
    def test_valid_json(self):
        v = AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator()
        ok, err = v.validate("inst-1", "https://a.com", '{"event": "push"}')
        assert ok is True
        assert err == ""

    def test_invalid_json(self):
        v = AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator()
        ok, err = v.validate("inst-1", "https://a.com", "not json")
        assert ok is False
        assert "Invalid JSON" in err

    def test_too_large(self):
        v = AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator(max_payload_bytes=10)
        ok, err = v.validate("inst-1", "https://a.com", '{"data": "large payload"}')
        assert ok is False
        assert "too large" in err

    def test_stats(self):
        v = AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator()
        v.validate("inst-1", "https://a.com", '{"ok": true}')
        v.validate("inst-1", "https://a.com", "bad")
        s = v.stats("inst-1", "https://a.com")
        assert s.valid_rate == 50.0

    def test_isolation(self):
        v = AppAPIDeveloperPlatformSDKApiWebhookPayloadValidator()
        v.validate("inst-1", "https://a.com", "{}")
        assert len(v.all_validations("inst-2")) == 0
