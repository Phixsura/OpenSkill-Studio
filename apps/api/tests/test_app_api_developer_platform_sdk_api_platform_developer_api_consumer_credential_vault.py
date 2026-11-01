import pytest
from app.services.app_api_developer_platform_sdk_api_platform_developer_api_consumer_credential_vault import AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault

class TestConsumerCredentialVault:
    def test_store_and_verify(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        entry = svc.store("inst-1", "c1", "k1", "api_key", "my-secret-api-key-1234")
        assert entry.masked_value == "***1234"
        assert svc.verify("inst-1", "c1", "k1", "my-secret-api-key-1234") is True
        assert svc.verify("inst-1", "c1", "k1", "wrong-key") is False

    def test_no_plaintext_stored(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        entry = svc.store("inst-1", "c1", "k1", "webhook_secret", "super-secret-webhook")
        assert "super-secret-webhook" not in entry.masked_value
        assert "super-secret-webhook" not in entry.hash_value

    def test_rotate(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        svc.store("inst-1", "c1", "k1", "api_key", "old-key-12345678")
        new = svc.rotate("inst-1", "c1", "k1", "new-key-87654321")
        assert svc.verify("inst-1", "c1", "k1", "new-key-87654321") is True
        assert svc.verify("inst-1", "c1", "k1", "old-key-12345678") is False

    def test_short_credential_rejected(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        with pytest.raises(ValueError, match="at least 8"):
            svc.store("inst-1", "c1", "k1", "api_key", "short")

    def test_revoke(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        svc.store("inst-1", "c1", "k1", "api_key", "my-api-key-value")
        assert svc.revoke("inst-1", "c1", "k1") is True
        assert svc.verify("inst-1", "c1", "k1", "my-api-key-value") is False

    def test_isolation(self):
        svc = AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault()
        svc.store("inst-1", "c1", "k1", "api_key", "my-api-key-value")
        assert svc.entry_count("inst-2") == 0
