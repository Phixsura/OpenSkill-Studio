import pytest
from app.services.app_api_developer_platform_sdk_api_developer_api_webhook_error_classifier import AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier

class TestWebhookErrorClassifier:
    def test_classify(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier()
        e = c.classify("inst-1", "timeout", "https://a.com")
        assert e.count == 1

    def test_accumulate(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier()
        c.classify("inst-1", "timeout", "https://a.com")
        c.classify("inst-1", "timeout", "https://b.com")
        e = c.by_class("inst-1", "timeout")
        assert e.count == 2
        assert len(e.destinations_affected) == 2

    def test_invalid_class(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier()
        with pytest.raises(ValueError):
            c.classify("inst-1", "unknown_error", "https://a.com")

    def test_top_errors(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier()
        for _ in range(10): c.classify("inst-1", "timeout", "https://a.com")
        for _ in range(5): c.classify("inst-1", "http_5xx", "https://b.com")
        top = c.top_errors("inst-1")
        assert top[0].error_class == "timeout"

    def test_isolation(self):
        c = AppAPIDeveloperPlatformSDKApiDeveloperApiWebhookErrorClassifier()
        c.classify("inst-1", "timeout", "https://a.com")
        assert c.total_errors("inst-2") == 0
