import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_api_consumer_api_api_payload_encryption import (
    AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption, EncryptionConfig,
)

class TestPayloadEncryption:
    def test_encrypt_fields(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(consumer_id="c1", encrypted_fields=["ssn", "email"]))
        result, info = svc.encrypt_fields("inst-1", "c1", {"ssn": "123-45-6789", "email": "a@b.com", "name": "Alice"})
        assert result["ssn"].startswith("enc:")
        assert result["email"].startswith("enc:")
        assert result["name"] == "Alice"  # not encrypted
        assert info.encrypted_field_count == 2

    def test_no_config_passthrough(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption()
        result, info = svc.encrypt_fields("inst-1", "c1", {"data": "test"})
        assert result["data"] == "test"
        assert info.encrypted_field_count == 0

    def test_invalid_algorithm(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption()
        with pytest.raises(ValueError, match="Invalid algorithm"):
            svc.configure("inst-1", EncryptionConfig(consumer_id="c1", algorithm="rot13", encrypted_fields=["x"]))

    def test_stats(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(consumer_id="c1", encrypted_fields=["ssn"]))
        svc.encrypt_fields("inst-1", "c1", {"ssn": "123"})
        assert svc.stats("inst-1")["fields"] == 1

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiPayloadEncryption()
        svc.configure("inst-1", EncryptionConfig(consumer_id="c1", encrypted_fields=["x"]))
        assert len(svc.list_configs("inst-2")) == 0
