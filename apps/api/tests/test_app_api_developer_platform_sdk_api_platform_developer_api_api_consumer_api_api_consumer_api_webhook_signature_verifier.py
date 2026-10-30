import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_consumer_api_webhook_signature_verifier import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier, VerifierConfig,
)

class TestWebhookSignatureVerifier:
    def test_sign_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="s3cret"))
        sig = svc.sign("inst-1", "wh1", 1000000, '{"event":"test"}')
        result = svc.verify("inst-1", "wh1", 1000000, '{"event":"test"}', sig, now=1000010)
        assert result.valid and result.reason == "valid"

    def test_invalid_signature(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="s3cret"))
        result = svc.verify("inst-1", "wh1", 1000000, '{"event":"test"}', "badsig", now=1000010)
        assert not result.valid and result.reason == "invalid_signature"

    def test_expired_timestamp(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="s3cret", tolerance_seconds=60))
        sig = svc.sign("inst-1", "wh1", 1000000, "body")
        result = svc.verify("inst-1", "wh1", 1000000, "body", sig, now=1000100)
        assert not result.valid and result.reason == "expired_timestamp"

    def test_replay_detected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="s3cret"))
        sig = svc.sign("inst-1", "wh1", 1000000, "body")
        svc.verify("inst-1", "wh1", 1000000, "body", sig, now=1000010)
        result = svc.verify("inst-1", "wh1", 1000000, "body", sig, now=1000020)
        assert not result.valid and result.reason == "replay_detected"

    def test_sha512(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="key", algorithm="sha512"))
        sig = svc.sign("inst-1", "wh1", 100, "data")
        result = svc.verify("inst-1", "wh1", 100, "data", sig, now=110)
        assert result.valid

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiWebhookSignatureVerifier()
        svc.set_config("inst-1", VerifierConfig(webhook_id="wh1", secret="key"))
        result = svc.verify("inst-2", "wh1", 100, "data", "sig", now=110)
        assert not result.valid and result.reason == "missing_header"
