"""Tests for App Credential Vault — store, verify, rotate, metadata."""

import pytest

from app.services.app_credential_vault import AppCredentialVault


class TestStore:
    def test_store(self):
        v = AppCredentialVault()
        c = v.store("inst-1", "db-password", "Database Password", "super_secret_password_123")
        assert c.credential_id == "db-password"
        assert c.prefix == "supe"
        assert len(c.value_hash) == 64

    def test_short_value(self):
        v = AppCredentialVault()
        with pytest.raises(ValueError, match="8 characters"):
            v.store("inst-1", "c1", "Short", "abc")

    def test_duplicate(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Cred", "password_123")
        with pytest.raises(ValueError, match="rotate"):
            v.store("inst-1", "c1", "Cred2", "other_pass_456")


class TestMetadata:
    def test_get_metadata(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "API Key", "sk_live_abcdef123456")
        meta = v.get_metadata("inst-1", "c1")
        assert meta.name == "API Key"
        assert meta.prefix == "sk_l"

    def test_not_found(self):
        v = AppCredentialVault()
        with pytest.raises(KeyError):
            v.get_metadata("inst-1", "nope")


class TestVerify:
    def test_correct(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Key", "my_secret_key_value")
        assert v.verify("inst-1", "c1", "my_secret_key_value") is True

    def test_wrong(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Key", "my_secret_key_value")
        assert v.verify("inst-1", "c1", "wrong_value") is False

    def test_missing(self):
        v = AppCredentialVault()
        assert v.verify("inst-1", "nope", "val") is False


class TestRotate:
    def test_rotate(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Key", "old_password_1234")
        c = v.rotate("inst-1", "c1", "new_password_5678", now=2000.0)
        assert c.version == 2
        assert c.rotated_at == 2000.0
        assert v.verify("inst-1", "c1", "new_password_5678") is True
        assert v.verify("inst-1", "c1", "old_password_1234") is False


class TestDelete:
    def test_delete(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Key", "password_1234")
        assert v.delete("inst-1", "c1") is True
        assert v.list_credentials("inst-1") == []


class TestIsolation:
    def test_cross_installation(self):
        v = AppCredentialVault()
        v.store("inst-1", "c1", "Key", "password_1234")
        with pytest.raises(KeyError):
            v.get_metadata("inst-2", "c1")
