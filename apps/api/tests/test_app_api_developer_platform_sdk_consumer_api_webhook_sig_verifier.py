"""Tests for Webhook Signature Verifier service."""
import pytest
from app.services.app_api_developer_platform_sdk_consumer_api_webhook_sig_verifier import SignatureVerifier


class TestSignatureVerifier:
    def test_sign_and_verify(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        signed = svc.sign("wh1", '{"event":"test"}', timestamp=1000.0, nonce="n1")
        result = svc.verify("wh1", '{"event":"test"}', signed["signature"],
                            1000.0, "n1", current_time=1000.0)
        assert result["valid"] is True

    def test_signature_mismatch(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        result = svc.verify("wh1", '{"event":"test"}', "bad-signature",
                            1000.0, "n1", current_time=1000.0)
        assert result["valid"] is False
        assert result["reason"] == "signature_mismatch"

    def test_timestamp_expired(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        signed = svc.sign("wh1", "payload", timestamp=1000.0, nonce="n1")
        result = svc.verify("wh1", "payload", signed["signature"],
                            1000.0, "n1", current_time=2000.0)
        assert result["valid"] is False
        assert result["reason"] == "timestamp_expired"

    def test_nonce_replay(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        signed = svc.sign("wh1", "data", timestamp=100.0, nonce="n1")
        svc.verify("wh1", "data", signed["signature"], 100.0, "n1", current_time=100.0)
        result = svc.verify("wh1", "data", signed["signature"], 100.0, "n1", current_time=100.0)
        assert result["valid"] is False
        assert result["reason"] == "nonce_reused"

    def test_sha512(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        signed = svc.sign("wh1", "payload", timestamp=100.0, nonce="n1", algorithm="sha512")
        result = svc.verify("wh1", "payload", signed["signature"],
                            100.0, "n1", algorithm="sha512", current_time=100.0)
        assert result["valid"] is True
        assert result["algorithm"] == "sha512"

    def test_unknown_webhook(self):
        svc = SignatureVerifier()
        assert svc.verify("unknown", "x", "sig", 0, "n")["reason"] == "unknown_webhook"

    def test_short_secret_rejected(self):
        svc = SignatureVerifier()
        with pytest.raises(ValueError):
            svc.register_secret("wh1", "short")

    def test_cleanup_nonces(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "super-secret-key-1234")
        signed = svc.sign("wh1", "d", timestamp=100.0, nonce="n1")
        svc.verify("wh1", "d", signed["signature"], 100.0, "n1", current_time=100.0)
        result = svc.cleanup_nonces(max_age=50, current_time=200.0)
        assert result["removed"] == 1

    def test_rotate_secret(self):
        svc = SignatureVerifier()
        svc.register_secret("wh1", "original-secret-key!!")
        r = svc.rotate_secret("wh1", "new-rotated-secret!!")
        assert r["rotated"] is True
        assert r["had_previous"] is True

    def test_isolation(self):
        a, b = SignatureVerifier(), SignatureVerifier()
        a.register_secret("wh1", "secret-key-abcdefgh")
        assert b.verify("wh1", "x", "s", 0, "n")["reason"] == "unknown_webhook"
