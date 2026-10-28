"""Tests for App API Key Rotation — generate, verify, rotate, revoke."""

import pytest

from app.services.app_api_key_rotation import AppAPIKeyRotation


class TestGenerate:
    def test_generate(self):
        r = AppAPIKeyRotation()
        key, raw = r.generate_key("inst-1", "k1", label="Production")
        assert key.prefix == raw[:8]
        assert key.label == "Production"
        assert key.is_active is True

    def test_with_ttl(self):
        r = AppAPIKeyRotation()
        key, _ = r.generate_key("inst-1", "k1", ttl_seconds=3600)
        assert key.expires_at is not None

    def test_invalid_ttl(self):
        r = AppAPIKeyRotation()
        with pytest.raises(ValueError, match="positive"):
            r.generate_key("inst-1", "k1", ttl_seconds=0)


class TestVerify:
    def test_verify_valid(self):
        r = AppAPIKeyRotation()
        _, raw = r.generate_key("inst-1", "k1")
        result = r.verify("inst-1", raw)
        assert result is not None
        assert result.key_id == "k1"

    def test_verify_invalid(self):
        r = AppAPIKeyRotation()
        r.generate_key("inst-1", "k1")
        assert r.verify("inst-1", "bad-key") is None

    def test_verify_revoked(self):
        r = AppAPIKeyRotation()
        _, raw = r.generate_key("inst-1", "k1")
        r.revoke("inst-1", "k1")
        assert r.verify("inst-1", raw) is None


class TestRotate:
    def test_rotate(self):
        r = AppAPIKeyRotation()
        r.generate_key("inst-1", "k1", label="Prod")
        new_key, new_raw = r.rotate("inst-1", "k1", "k2", grace_seconds=60)
        assert new_key.key_id == "k2"
        # Old key should still be active (grace period)
        old = r.list_keys("inst-1")
        old_key = [k for k in old if k.key_id == "k1"][0]
        assert old_key.expires_at is not None
        assert old_key.is_active is True


class TestRevoke:
    def test_revoke(self):
        r = AppAPIKeyRotation()
        r.generate_key("inst-1", "k1")
        k = r.revoke("inst-1", "k1")
        assert k.revoked is True
        assert k.is_active is False


class TestIsolation:
    def test_cross(self):
        r = AppAPIKeyRotation()
        r.generate_key("inst-1", "k1")
        assert r.list_keys("inst-2") == []
