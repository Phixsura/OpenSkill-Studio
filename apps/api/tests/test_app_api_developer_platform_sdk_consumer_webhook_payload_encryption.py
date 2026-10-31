import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_consumer_endpoint_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_consumer_api_webhook_payload_encryption import (
    AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption, EncryptionConfig,
)

class TestWebhookPayloadEncryption:
    def test_encrypt(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1", algorithm="aes-256-gcm"))
        result = svc.encrypt("inst-1", "c1", "w1", '{"event":"test"}')
        assert result is not None and result.algorithm == "aes-256-gcm" and len(result.ciphertext) > 0

    def test_none_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1", algorithm="none"))
        assert svc.encrypt("inst-1", "c1", "w1", "test") is None

    def test_disabled(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1", enabled=False))
        assert svc.encrypt("inst-1", "c1", "w1", "test") is None

    def test_is_enabled(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1"))
        assert svc.is_encryption_enabled("inst-1", "c1", "w1")
        assert not svc.is_encryption_enabled("inst-1", "c1", "unconfigured")

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        with pytest.raises(ValueError, match="Invalid algorithm"):
            svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1", algorithm="des"))

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiWebhookPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(webhook_id="w1", consumer_id="c1"))
        assert svc.get_config("inst-2", "c1", "w1") is None
