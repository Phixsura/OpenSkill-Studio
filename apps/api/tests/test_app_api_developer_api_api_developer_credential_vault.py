import pytest
from app.services.app_api_developer_api_api_developer_credential_vault import AppAPIDeveloperAPIApiDeveloperCredentialVault

class TestCredentialVault:
    def test_store(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        e = v.store("inst-1", "e1", "api_key", "Prod Key", "sk-prod-abcdefghijklmnop")
        assert len(e.fingerprint) == 16

    def test_short_credential(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        with pytest.raises(ValueError, match="too short"):
            v.store("inst-1", "e1", "api_key", "Key", "short")

    def test_access(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        v.store("inst-1", "e1", "api_key", "Key", "long-credential-value")
        e = v.access("inst-1", "e1")
        assert e.access_count == 1
        assert e.last_accessed_at is not None

    def test_rotate(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        v.store("inst-1", "e1", "webhook_secret", "Secret", "old-secret-value-long")
        old_fp = v.list_entries("inst-1")[0].fingerprint
        v.rotate("inst-1", "e1", "new-secret-value-long")
        new_fp = v.list_entries("inst-1")[0].fingerprint
        assert old_fp != new_fp
        assert v.list_entries("inst-1")[0].rotated is True

    def test_by_type(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        v.store("inst-1", "e1", "api_key", "K1", "key-value-1234567")
        v.store("inst-1", "e2", "webhook_secret", "S1", "secret-value-1234")
        assert len(v.by_type("inst-1", "api_key")) == 1

    def test_isolation(self):
        v = AppAPIDeveloperAPIApiDeveloperCredentialVault()
        v.store("inst-1", "e1", "api_key", "Key", "credential-value-xyz")
        assert len(v.list_entries("inst-2")) == 0
