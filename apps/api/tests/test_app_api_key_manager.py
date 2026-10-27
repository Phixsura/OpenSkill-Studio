"""Tests for App API Key Manager — create, validate, rotate, revoke, scopes."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_api_key_manager import (
    AppApiKeyManager,
    KeyStatus,
)


class TestCreate:
    def test_create_returns_raw_and_record(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"])
        assert raw.startswith("osk_")
        assert key.key_id is not None
        assert key.installation_id == "inst-1"
        assert key.scopes == ["read:skills"]
        assert key.status == KeyStatus.ACTIVE

    def test_raw_key_not_stored(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"])
        # Raw should not appear in any stored key
        for stored in m._keys.values():
            assert raw not in stored.key_hash
            assert raw not in stored.key_prefix  # prefix is truncated

    def test_no_scopes_rejected(self):
        m = AppApiKeyManager()
        with pytest.raises(ValueError, match="scope"):
            m.create("inst-1", "app-1", [])

    def test_with_ttl(self):
        m = AppApiKeyManager()
        _, key = m.create("inst-1", "app-1", ["read:skills"], ttl_days=30)
        assert key.expires_at is not None

    def test_unique_keys(self):
        m = AppApiKeyManager()
        raw1, _ = m.create("inst-1", "app-1", ["read:skills"])
        raw2, _ = m.create("inst-1", "app-1", ["read:skills"])
        assert raw1 != raw2


class TestValidate:
    def test_valid_key(self):
        m = AppApiKeyManager()
        raw, _ = m.create("inst-1", "app-1", ["read:skills", "write:projects"])
        result = m.validate(raw)
        assert result.valid is True
        assert "read:skills" in result.scopes

    def test_invalid_key(self):
        m = AppApiKeyManager()
        result = m.validate("osk_fake_key_that_doesnt_exist")
        assert result.valid is False
        assert "Invalid" in result.error

    def test_scope_check_pass(self):
        m = AppApiKeyManager()
        raw, _ = m.create("inst-1", "app-1", ["read:skills"])
        result = m.validate(raw, required_scope="read:skills")
        assert result.valid is True

    def test_scope_check_fail(self):
        m = AppApiKeyManager()
        raw, _ = m.create("inst-1", "app-1", ["read:skills"])
        result = m.validate(raw, required_scope="admin:org")
        assert result.valid is False
        assert "Missing scope" in result.error

    def test_expired_key(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"], ttl_days=1)
        future = datetime.now(UTC) + timedelta(days=2)
        result = m.validate(raw, now=future)
        assert result.valid is False
        assert "expired" in result.error.lower()

    def test_updates_last_used(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"])
        assert key.last_used_at is None
        m.validate(raw)
        assert key.last_used_at is not None


class TestRevoke:
    def test_revoke(self):
        m = AppApiKeyManager()
        _, key = m.create("inst-1", "app-1", ["read:skills"])
        assert m.revoke(key.key_id) is True

    def test_revoked_key_invalid(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"])
        m.revoke(key.key_id)
        result = m.validate(raw)
        assert result.valid is False
        assert "revoked" in result.error.lower()

    def test_revoke_nonexistent(self):
        m = AppApiKeyManager()
        assert m.revoke("key-999") is False


class TestRotate:
    def test_rotate_creates_new(self):
        m = AppApiKeyManager()
        raw_old, _ = m.create("inst-1", "app-1", ["read:skills"])
        result = m.rotate(raw_old)
        assert result is not None
        raw_new, new_key = result
        assert raw_new != raw_old
        assert new_key.scopes == ["read:skills"]

    def test_old_key_still_valid_during_overlap(self):
        m = AppApiKeyManager()
        raw_old, _ = m.create("inst-1", "app-1", ["read:skills"])
        m.rotate(raw_old, overlap_hours=24)
        result = m.validate(raw_old)
        assert result.valid is True  # overlap period

    def test_rotate_with_new_scopes(self):
        m = AppApiKeyManager()
        raw_old, _ = m.create("inst-1", "app-1", ["read:skills"])
        result = m.rotate(raw_old, new_scopes=["read:skills", "write:projects"])
        _, new_key = result
        assert "write:projects" in new_key.scopes

    def test_rotate_invalid_key(self):
        m = AppApiKeyManager()
        assert m.rotate("osk_fake") is None

    def test_rotate_revoked_key(self):
        m = AppApiKeyManager()
        raw, key = m.create("inst-1", "app-1", ["read:skills"])
        m.revoke(key.key_id)
        assert m.rotate(raw) is None


class TestListing:
    def test_list_keys(self):
        m = AppApiKeyManager()
        m.create("inst-1", "app-1", ["read:skills"])
        m.create("inst-1", "app-1", ["write:projects"])
        m.create("inst-2", "app-1", ["read:skills"])
        keys = m.list_keys("inst-1")
        assert len(keys) == 2

    def test_active_count(self):
        m = AppApiKeyManager()
        m.create("inst-1", "app-1", ["read:skills"])
        _, key2 = m.create("inst-1", "app-1", ["read:skills"])
        m.revoke(key2.key_id)
        assert m.get_active_count("inst-1") == 1

    def test_newest_first(self):
        m = AppApiKeyManager()
        m.create("inst-1", "app-1", ["a"])
        m.create("inst-1", "app-1", ["b"])
        keys = m.list_keys("inst-1")
        assert keys[0].key_id == "key-2"  # newest
