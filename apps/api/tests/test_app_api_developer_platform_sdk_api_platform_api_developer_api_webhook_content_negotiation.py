import pytest
from app.services.app_api_developer_platform_sdk_api_platform_api_developer_api_webhook_content_negotiation import AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation

class TestContentNegotiation:
    def test_configure(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        cn = n.configure("inst-1", "c1", "application/json")
        assert cn.preferred_format == "application/json"

    def test_unsupported_format(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        with pytest.raises(ValueError):
            n.configure("inst-1", "c1", "text/html")

    def test_negotiate_preferred(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        n.configure("inst-1", "c1", "application/xml", ["application/xml", "application/json"])
        result = n.negotiate("inst-1", "c1", ["application/json", "application/xml"])
        assert result == "application/xml"

    def test_negotiate_fallback(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        n.configure("inst-1", "c1", "application/xml")
        result = n.negotiate("inst-1", "c1", ["text/plain"])
        assert result == "application/json"  # fallback

    def test_format_distribution(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        n.configure("inst-1", "c1", "application/json")
        n.configure("inst-1", "c2", "application/xml")
        dist = n.format_distribution("inst-1")
        assert dist == {"application/json": 1, "application/xml": 1}

    def test_isolation(self):
        n = AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiWebhookContentNegotiation()
        n.configure("inst-1", "c1", "application/json")
        assert len(n.all_negotiations("inst-2")) == 0
