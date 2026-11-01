import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_consumer_api_api_consumer_api_webhook_security import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity, WebhookSecurityPolicy,
)

class TestConsumerApiWebhookSecurity:
    def test_perfect_score(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        svc.set_policy("inst-1", WebhookSecurityPolicy(webhook_id="w1", consumer_id="c1", ip_whitelist=["10.0.0.0/8"]))
        result = svc.audit("inst-1", "c1", "w1", "https://hook.example.com")
        assert result.score == 100 and result.compliant

    def test_http_penalty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        svc.set_policy("inst-1", WebhookSecurityPolicy(webhook_id="w1", consumer_id="c1", ip_whitelist=["10.0.0.0/8"]))
        result = svc.audit("inst-1", "c1", "w1", "http://insecure.com")
        assert result.score < 100 and "HTTPS" in result.issues[0]

    def test_no_policy(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        result = svc.audit("inst-1", "c1", "missing", "https://x.com")
        assert result.score == 50 and not result.compliant

    def test_no_signature_penalty(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        svc.set_policy("inst-1", WebhookSecurityPolicy(webhook_id="w1", consumer_id="c1", require_signature=False, ip_whitelist=["x"]))
        result = svc.audit("inst-1", "c1", "w1", "https://x.com")
        assert result.score < 100

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        with pytest.raises(ValueError, match="Unsupported algorithm"):
            svc.set_policy("inst-1", WebhookSecurityPolicy(webhook_id="w1", consumer_id="c1", signature_algorithm="md5"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity()
        svc.set_policy("inst-1", WebhookSecurityPolicy(webhook_id="w1", consumer_id="c1"))
        assert svc.get_policy("inst-2", "c1", "w1") is None
