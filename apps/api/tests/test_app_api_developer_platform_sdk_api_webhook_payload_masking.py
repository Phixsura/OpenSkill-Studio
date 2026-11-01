from app.services.app_api_developer_platform_sdk_api_webhook_payload_masking import AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking

class TestPayloadMasking:
    def test_custom_mask(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        m.configure("inst-1", "https://a.com", [{"field_pattern": "api_key"}])
        result = m.mask("inst-1", "https://a.com", {"api_key": "sk-1234567890", "name": "test"})
        assert result["api_key"].endswith("7890")
        assert result["api_key"].startswith("*")
        assert result["name"] == "test"

    def test_default_mask(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        result = m.mask("inst-1", "https://unknown.com", {"password": "secret123", "name": "test"})
        assert result["password"] == "[MASKED]"
        assert result["name"] == "test"

    def test_short_value(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        m.configure("inst-1", "https://a.com", [{"field_pattern": "pin", "visible_chars": 4}])
        result = m.mask("inst-1", "https://a.com", {"pin": "12"})
        assert result["pin"] == "[MASKED]"

    def test_masked_count(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        m.configure("inst-1", "https://a.com", [{"field_pattern": "secret"}])
        m.mask("inst-1", "https://a.com", {"secret": "value12345"})
        m.mask("inst-1", "https://a.com", {"secret": "other12345"})
        assert m.all_configs("inst-1")[0].masked_count == 2

    def test_isolation(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        m.configure("inst-1", "https://a.com", [])
        assert len(m.all_configs("inst-2")) == 0

    def test_negative_visible_chars_rejected(self):
        import pytest
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        with pytest.raises(ValueError, match="visible_chars"):
            m.configure("inst-1", "https://a.com", [{"field_pattern": "key", "visible_chars": -1}])

    def test_zero_visible_chars(self):
        m = AppAPIDeveloperPlatformSDKApiWebhookPayloadMasking()
        m.configure("inst-1", "https://a.com", [{"field_pattern": "secret", "visible_chars": 0}])
        result = m.mask("inst-1", "https://a.com", {"secret": "mysecretvalue"})
        assert result["secret"] == "*" * 13
