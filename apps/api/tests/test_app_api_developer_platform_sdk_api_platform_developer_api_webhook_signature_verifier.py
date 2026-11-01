import pytest, time
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_webhook_signature_verifier import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier

class TestWebhookSignatureVerifier:
    def test_sign_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier()
        svc.configure("inst-1", "c1", "a-very-secure-secret-key-1234")
        sig = svc.sign("inst-1", "c1", '{"event":"test"}')
        result = svc.verify("inst-1", "c1", '{"event":"test"}', sig)
        assert result.valid is True

    def test_tampered_payload(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier()
        svc.configure("inst-1", "c1", "a-very-secure-secret-key-1234")
        sig = svc.sign("inst-1", "c1", '{"event":"test"}')
        result = svc.verify("inst-1", "c1", '{"event":"hacked"}', sig)
        assert result.valid is False
        assert result.reason == "invalid_signature"

    def test_expired_timestamp(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier()
        svc.configure("inst-1", "c1", "a-very-secure-secret-key-1234", timestamp_tolerance_s=10)
        old_ts = int(time.time()) - 100
        sig = svc.sign("inst-1", "c1", "test", old_ts)
        result = svc.verify("inst-1", "c1", "test", sig)
        assert result.valid is False and result.reason == "expired_timestamp"

    def test_short_secret_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier()
        with pytest.raises(ValueError, match="at least 16"):
            svc.configure("inst-1", "c1", "short")

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookSignatureVerifier()
        svc.configure("inst-1", "c1", "a-very-secure-secret-key-1234")
        assert len(svc.list_configs("inst-2")) == 0
