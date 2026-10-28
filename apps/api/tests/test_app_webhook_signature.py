"""Tests for App Webhook Signature — sign, verify, key rotation."""

import pytest

from app.services.app_webhook_signature import AppWebhookSignature

SECRET = "super-secret-key-1234"


class TestAddKey:
    def test_add(self):
        s = AppWebhookSignature()
        k = s.add_key("inst-1", "k1", SECRET)
        assert k.active is True

    def test_short_secret(self):
        s = AppWebhookSignature()
        with pytest.raises(ValueError, match="at least 16"):
            s.add_key("inst-1", "k1", "short")


class TestSign:
    def test_sign(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        result = s.sign("inst-1", "k1", '{"event":"push"}')
        assert len(result.signature) == 64  # SHA-256 hex
        assert result.algorithm == "hmac-sha256"

    def test_inactive_key(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        s.deactivate_key("inst-1", "k1")
        with pytest.raises(ValueError, match="not active"):
            s.sign("inst-1", "k1", "payload")


class TestVerify:
    def test_verify_valid(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        result = s.sign("inst-1", "k1", "payload")
        assert s.verify("inst-1", "payload", result.signature) is True

    def test_verify_invalid(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        assert s.verify("inst-1", "payload", "bad-sig") is False

    def test_verify_rotated_key(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        s.add_key("inst-1", "k2", "another-secret-key-5678")
        result = s.sign("inst-1", "k1", "payload")
        # Should verify against k1 even if k2 also active
        assert s.verify("inst-1", "payload", result.signature) is True


class TestDeactivate:
    def test_deactivated_not_verified(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        result = s.sign("inst-1", "k1", "payload")
        s.deactivate_key("inst-1", "k1")
        assert s.verify("inst-1", "payload", result.signature) is False


class TestIsolation:
    def test_cross(self):
        s = AppWebhookSignature()
        s.add_key("inst-1", "k1", SECRET)
        assert s.list_keys("inst-2") == []
