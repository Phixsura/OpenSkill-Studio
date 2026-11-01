"""Tests for App Secret Manager — CRUD, rotation, TTL, limits, audit."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.app_secret_manager import (
    MAX_SECRET_KEY_LENGTH,
    MAX_SECRET_VALUE_LENGTH,
    MAX_SECRETS_PER_INSTALL,
    AppSecretManager,
    SecretAccessType,
)


class TestSetAndGet:
    def test_set_and_get(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "API_KEY", "sk-12345", actor_id="admin")
        r = sm.get_secret("inst-1", "API_KEY", actor_id="admin")
        assert r.success is True
        assert r.value == "sk-12345"
        assert r.version == 1

    def test_update_increments_version(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "API_KEY", "v1", actor_id="admin")
        sm.set_secret("inst-1", "API_KEY", "v2", actor_id="admin")
        r = sm.get_secret("inst-1", "API_KEY", actor_id="admin")
        assert r.value == "v2"
        assert r.version == 2

    def test_get_nonexistent(self):
        sm = AppSecretManager()
        r = sm.get_secret("inst-1", "NOPE", actor_id="admin")
        assert r.success is False
        assert "not found" in r.error

    def test_cross_installation_isolated(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val-1", actor_id="admin")
        sm.set_secret("inst-2", "KEY", "val-2", actor_id="admin")
        assert sm.get_secret("inst-1", "KEY", "admin").value == "val-1"
        assert sm.get_secret("inst-2", "KEY", "admin").value == "val-2"


class TestValidation:
    def test_empty_key_rejected(self):
        sm = AppSecretManager()
        r = sm.set_secret("inst-1", "", "value", actor_id="admin")
        assert r.success is False

    def test_long_key_rejected(self):
        sm = AppSecretManager()
        r = sm.set_secret("inst-1", "K" * (MAX_SECRET_KEY_LENGTH + 1), "val", actor_id="admin")
        assert r.success is False

    def test_long_value_rejected(self):
        sm = AppSecretManager()
        r = sm.set_secret("inst-1", "KEY", "V" * (MAX_SECRET_VALUE_LENGTH + 1), actor_id="admin")
        assert r.success is False

    def test_count_limit(self):
        sm = AppSecretManager()
        for i in range(MAX_SECRETS_PER_INSTALL):
            r = sm.set_secret("inst-1", f"KEY_{i}", f"val_{i}", actor_id="admin")
            assert r.success is True
        r = sm.set_secret("inst-1", "ONE_MORE", "val", actor_id="admin")
        assert r.success is False
        assert "Limit" in r.error

    def test_update_doesnt_count_as_new(self):
        sm = AppSecretManager()
        for i in range(MAX_SECRETS_PER_INSTALL):
            sm.set_secret("inst-1", f"KEY_{i}", f"val_{i}", actor_id="admin")
        # Updating an existing one should work
        r = sm.set_secret("inst-1", "KEY_0", "updated", actor_id="admin")
        assert r.success is True


class TestRotation:
    def test_rotate_sets_new_value(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "old-value", actor_id="admin")
        r = sm.rotate_secret("inst-1", "KEY", "new-value", actor_id="admin")
        assert r.success is True
        assert r.version == 2
        assert sm.get_secret("inst-1", "KEY", "admin").value == "new-value"

    def test_previous_value_readable_during_grace(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "old-value", actor_id="admin")
        sm.rotate_secret("inst-1", "KEY", "new-value", actor_id="admin", grace_seconds=600)
        r = sm.get_previous_value("inst-1", "KEY", actor_id="admin")
        assert r.success is True
        assert r.value == "old-value"

    def test_previous_value_expired(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "old-value", actor_id="admin")
        sm.rotate_secret("inst-1", "KEY", "new-value", actor_id="admin", grace_seconds=1)
        # Manually expire
        entry = sm._secrets[("inst-1", "KEY")]
        entry.previous_expires_at = datetime.now(UTC) - timedelta(seconds=1)
        r = sm.get_previous_value("inst-1", "KEY", actor_id="admin")
        assert r.success is False

    def test_rotate_nonexistent(self):
        sm = AppSecretManager()
        r = sm.rotate_secret("inst-1", "NOPE", "val", actor_id="admin")
        assert r.success is False

    def test_rotate_long_value_rejected(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin")
        r = sm.rotate_secret("inst-1", "KEY", "V" * (MAX_SECRET_VALUE_LENGTH + 1), actor_id="admin")
        assert r.success is False


class TestTTL:
    def test_expired_secret_removed_on_read(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin", ttl_seconds=1)
        # Manually expire
        entry = sm._secrets[("inst-1", "KEY")]
        entry.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        r = sm.get_secret("inst-1", "KEY", actor_id="admin")
        assert r.success is False
        assert "expired" in r.error

    def test_non_expired_readable(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin", ttl_seconds=3600)
        r = sm.get_secret("inst-1", "KEY", actor_id="admin")
        assert r.success is True

    def test_expired_excluded_from_list(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "ALIVE", "val", actor_id="admin")
        sm.set_secret("inst-1", "DEAD", "val", actor_id="admin", ttl_seconds=1)
        entry = sm._secrets[("inst-1", "DEAD")]
        entry.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        listing = sm.list_secrets("inst-1")
        keys = [s.key for s in listing]
        assert "ALIVE" in keys
        assert "DEAD" not in keys


class TestDelete:
    def test_delete(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin")
        r = sm.delete_secret("inst-1", "KEY", actor_id="admin")
        assert r.success is True
        assert sm.get_secret("inst-1", "KEY", "admin").success is False

    def test_delete_nonexistent(self):
        sm = AppSecretManager()
        r = sm.delete_secret("inst-1", "NOPE", actor_id="admin")
        assert r.success is False

    def test_delete_all(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "A", "1", actor_id="admin")
        sm.set_secret("inst-1", "B", "2", actor_id="admin")
        count = sm.delete_all("inst-1", actor_id="admin")
        assert count == 2
        assert sm.count("inst-1") == 0


class TestListing:
    def test_list_returns_metadata(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY_A", "val-a", actor_id="admin")
        sm.set_secret("inst-1", "KEY_B", "val-b", actor_id="admin")
        listing = sm.list_secrets("inst-1")
        assert len(listing) == 2
        keys = [s.key for s in listing]
        assert "KEY_A" in keys
        # Values never in metadata
        assert all(not hasattr(s, "value") or "val" not in str(getattr(s, "value", "")) for s in listing)

    def test_list_shows_hash_prefix(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "secret-value", actor_id="admin")
        listing = sm.list_secrets("inst-1")
        assert len(listing[0].value_hash) == 16

    def test_list_has_previous_flag(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "old", actor_id="admin")
        sm.rotate_secret("inst-1", "KEY", "new", actor_id="admin", grace_seconds=600)
        listing = sm.list_secrets("inst-1")
        assert listing[0].has_previous is True

    def test_count(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "A", "1", actor_id="admin")
        sm.set_secret("inst-1", "B", "2", actor_id="admin")
        assert sm.count("inst-1") == 2
        assert sm.count("inst-2") == 0


class TestAuditLog:
    def test_access_logged(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="user-1")
        sm.get_secret("inst-1", "KEY", actor_id="user-2")
        log_entries = sm.get_access_log("inst-1")
        assert len(log_entries) == 2
        assert log_entries[0].access_type == SecretAccessType.WRITE
        assert log_entries[1].access_type == SecretAccessType.READ
        assert log_entries[1].actor_id == "user-2"

    def test_rotate_logged(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin")
        sm.rotate_secret("inst-1", "KEY", "new", actor_id="admin")
        log_entries = sm.get_access_log("inst-1")
        types = [e.access_type for e in log_entries]
        assert SecretAccessType.ROTATE in types

    def test_log_filtered_by_installation(self):
        sm = AppSecretManager()
        sm.set_secret("inst-1", "KEY", "val", actor_id="admin")
        sm.set_secret("inst-2", "KEY", "val", actor_id="admin")
        log_1 = sm.get_access_log("inst-1")
        assert len(log_1) == 1
