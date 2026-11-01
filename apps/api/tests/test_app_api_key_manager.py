"""Tests for App API Key Manager — create, validate, revoke, scope check."""

import pytest

from app.services.app_api_key_manager import AppApiKeyManager


class TestCreateKey:
    def test_create(self):
        m = AppApiKeyManager()
        record, raw_key = m.create_key("inst-1", "k1", "Production Key", scopes=["read", "write"])
        assert record.key_id == "k1"
        assert record.name == "Production Key"
        assert record.scopes == ["read", "write"]
        assert len(raw_key) > 20
        assert record.prefix == raw_key[:8]

    def test_duplicate_key_id(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key 1")
        with pytest.raises(ValueError, match="already exists"):
            m.create_key("inst-1", "k1", "Key 2")

    def test_missing_name(self):
        m = AppApiKeyManager()
        with pytest.raises(ValueError, match="name"):
            m.create_key("inst-1", "k1", "")

    def test_missing_installation_id(self):
        m = AppApiKeyManager()
        with pytest.raises(ValueError, match="installation_id"):
            m.create_key("", "k1", "Key")


class TestValidateKey:
    def test_valid_key(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", scopes=["read"])
        result = m.validate_key(raw)
        assert result.valid is True
        assert result.key_id == "k1"
        assert result.installation_id == "inst-1"

    def test_invalid_key(self):
        m = AppApiKeyManager()
        result = m.validate_key("bogus-key-value")
        assert result.valid is False
        assert result.reason == "key_not_found"

    def test_revoked_key(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key")
        m.revoke_key("inst-1", "k1")
        result = m.validate_key(raw)
        assert result.valid is False
        assert result.reason == "revoked"

    def test_expired_key(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", expires_in_seconds=60)
        record = m.get_key("inst-1", "k1")
        result = m.validate_key(raw, now=record.expires_at + 1)
        assert result.valid is False
        assert result.reason == "expired"

    def test_not_yet_expired(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", expires_in_seconds=3600)
        record = m.get_key("inst-1", "k1")
        result = m.validate_key(raw, now=record.created_at + 100)
        assert result.valid is True


class TestScopeCheck:
    def test_valid_scope(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", scopes=["read", "write"])
        result = m.validate_key(raw, required_scope="read")
        assert result.valid is True

    def test_insufficient_scope(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", scopes=["read"])
        result = m.validate_key(raw, required_scope="admin")
        assert result.valid is False
        assert result.reason == "insufficient_scope"

    def test_no_scope_required(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key", scopes=[])
        result = m.validate_key(raw)
        assert result.valid is True


class TestRevoke:
    def test_revoke(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key")
        record = m.revoke_key("inst-1", "k1")
        assert record.revoked is True
        assert record.revoked_at is not None

    def test_double_revoke(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key")
        m.revoke_key("inst-1", "k1")
        with pytest.raises(ValueError, match="already revoked"):
            m.revoke_key("inst-1", "k1")


class TestLastUsed:
    def test_tracks_last_used(self):
        m = AppApiKeyManager()
        _, raw = m.create_key("inst-1", "k1", "Key")
        m.validate_key(raw, now=1000.0)
        record = m.get_key("inst-1", "k1")
        assert record.last_used_at == 1000.0


class TestListKeys:
    def test_list_excludes_revoked(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key 1")
        m.create_key("inst-1", "k2", "Key 2")
        m.revoke_key("inst-1", "k2")
        keys = m.list_keys("inst-1")
        assert len(keys) == 1

    def test_list_includes_revoked(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key 1")
        m.create_key("inst-1", "k2", "Key 2")
        m.revoke_key("inst-1", "k2")
        keys = m.list_keys("inst-1", include_revoked=True)
        assert len(keys) == 2


class TestIsolation:
    def test_cross_installation(self):
        m = AppApiKeyManager()
        m.create_key("inst-1", "k1", "Key")
        with pytest.raises(KeyError):
            m.get_key("inst-2", "k1")
