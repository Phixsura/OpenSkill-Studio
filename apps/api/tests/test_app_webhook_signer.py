"""Tests for App Webhook Signer — sign, verify, rotation, replay."""

import pytest

from app.services.app_webhook_signer import AppWebhookSigner


class TestCreateSecret:
    def test_create(self):
        s = AppWebhookSigner()
        sec = s.create_secret("inst-1", "sec-1")
        assert sec.secret_id == "sec-1"
        assert len(sec.secret) == 64  # hex(32 bytes)
        assert sec.active is True

    def test_duplicate(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        with pytest.raises(ValueError, match="already exists"):
            s.create_secret("inst-1", "sec-1")

    def test_missing_installation_id(self):
        s = AppWebhookSigner()
        with pytest.raises(ValueError):
            s.create_secret("", "sec-1")


class TestSign:
    def test_sign_produces_v1_prefix(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        result = s.sign("inst-1", '{"event":"test"}', now=1000)
        assert result.signature.startswith("v1=")
        assert result.timestamp == 1000

    def test_sign_deterministic(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        r1 = s.sign("inst-1", "body", now=1000)
        r2 = s.sign("inst-1", "body", now=1000)
        assert r1.signature == r2.signature

    def test_sign_no_secret_raises(self):
        s = AppWebhookSigner()
        with pytest.raises(KeyError):
            s.sign("inst-1", "body")


class TestVerify:
    def test_valid_signature(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "payload", now=1000)
        result = s.verify("inst-1", "payload", signed.signature, signed.timestamp, now=1000)
        assert result.valid is True

    def test_invalid_signature(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        result = s.verify("inst-1", "payload", "v1=deadbeef", 1000, now=1000)
        assert result.valid is False
        assert result.reason == "invalid_signature"

    def test_wrong_body(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "original", now=1000)
        result = s.verify("inst-1", "tampered", signed.signature, signed.timestamp, now=1000)
        assert result.valid is False

    def test_no_v1_prefix(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        result = s.verify("inst-1", "body", "bad_format", 1000, now=1000)
        assert result.valid is False


class TestReplay:
    def test_expired_timestamp(self):
        s = AppWebhookSigner(tolerance_seconds=300)
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "body", now=1000)
        result = s.verify("inst-1", "body", signed.signature, signed.timestamp, now=1400)
        assert result.valid is False
        assert result.reason == "expired"

    def test_within_tolerance(self):
        s = AppWebhookSigner(tolerance_seconds=300)
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "body", now=1000)
        result = s.verify("inst-1", "body", signed.signature, signed.timestamp, now=1200)
        assert result.valid is True


class TestRotation:
    def test_rotate(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        new = s.rotate_secret("inst-1", "sec-1", "sec-2")
        assert new.active is True
        secrets = s.list_secrets("inst-1")
        old = [x for x in secrets if x.secret_id == "sec-1"][0]
        assert old.active is False

    def test_old_signature_invalid_after_rotation(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "body", now=1000)
        s.rotate_secret("inst-1", "sec-1", "sec-2")
        # Old secret deactivated, should not verify
        result = s.verify("inst-1", "body", signed.signature, signed.timestamp, now=1000)
        assert result.valid is False

    def test_no_secret_returns_no_secret(self):
        s = AppWebhookSigner()
        result = s.verify("inst-1", "body", "v1=abc", 1000, now=1000)
        assert result.valid is False
        assert result.reason == "no_secret"


class TestRevoke:
    def test_revoke(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        s.revoke_secret("inst-1", "sec-1")
        secrets = s.list_secrets("inst-1")
        assert secrets[0].active is False

    def test_revoke_nonexistent(self):
        s = AppWebhookSigner()
        with pytest.raises(KeyError):
            s.revoke_secret("inst-1", "nope")


class TestIsolation:
    def test_cross_installation(self):
        s = AppWebhookSigner()
        s.create_secret("inst-1", "sec-1")
        signed = s.sign("inst-1", "body", now=1000)
        result = s.verify("inst-2", "body", signed.signature, signed.timestamp, now=1000)
        assert result.valid is False
