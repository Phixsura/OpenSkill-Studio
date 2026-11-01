"""Tests for Webhook Signature Verifier — HMAC, replay protection, header parsing."""

import time

import pytest

from app.services.webhook_signature_verifier import (
    Algorithm,
    VerifyResult,
    WebhookSignatureVerifier,
    compute_hmac,
    compute_signed_payload,
    parse_signature_header,
)


class TestComputeHmac:
    def test_sha256_deterministic(self):
        sig1 = compute_hmac(b"payload", "secret")
        sig2 = compute_hmac(b"payload", "secret")
        assert sig1 == sig2

    def test_sha256_hex_length(self):
        sig = compute_hmac(b"payload", "secret", Algorithm.SHA256)
        assert len(sig) == 64

    def test_sha1_hex_length(self):
        sig = compute_hmac(b"payload", "secret", Algorithm.SHA1)
        assert len(sig) == 40

    def test_sha512_hex_length(self):
        sig = compute_hmac(b"payload", "secret", Algorithm.SHA512)
        assert len(sig) == 128

    def test_different_secrets_differ(self):
        s1 = compute_hmac(b"data", "key1")
        s2 = compute_hmac(b"data", "key2")
        assert s1 != s2

    def test_different_payloads_differ(self):
        s1 = compute_hmac(b"data1", "key")
        s2 = compute_hmac(b"data2", "key")
        assert s1 != s2


class TestParseSignatureHeader:
    def test_github_style(self):
        p = parse_signature_header("sha256=abc123def")
        assert p["algorithm"] == "sha256"
        assert p["signature"] == "abc123def"

    def test_stripe_style(self):
        p = parse_signature_header("t=1234567890,v1=abcdef")
        assert p["t"] == "1234567890"
        assert p["v1"] == "abcdef"

    def test_slack_style(self):
        p = parse_signature_header("v0=abcdef123")
        assert p["v0"] == "abcdef123"

    def test_plain_hex(self):
        p = parse_signature_header("abcdef123456")
        assert p["signature"] == "abcdef123456"

    def test_sha1_algorithm(self):
        p = parse_signature_header("sha1=abc")
        assert p["algorithm"] == "sha1"


class TestBasicVerification:
    def test_valid_signature(self):
        secret = "test-secret-key"
        payload = b'{"event": "test"}'
        sig = compute_hmac(payload, secret)
        v = WebhookSignatureVerifier(secret)
        result = v.verify(payload, f"sha256={sig}")
        assert result.result == VerifyResult.VALID

    def test_invalid_signature(self):
        v = WebhookSignatureVerifier("secret")
        result = v.verify(b"payload", "sha256=wrong_signature")
        assert result.result == VerifyResult.INVALID_SIGNATURE

    def test_missing_signature(self):
        v = WebhookSignatureVerifier("secret")
        result = v.verify(b"payload", "")
        assert result.result == VerifyResult.MISSING_SIGNATURE

    def test_sha1_valid(self):
        secret = "my-secret"
        payload = b"body"
        sig = compute_hmac(payload, secret, Algorithm.SHA1)
        v = WebhookSignatureVerifier(secret, Algorithm.SHA1)
        result = v.verify(payload, f"sha1={sig}")
        assert result.result == VerifyResult.VALID

    def test_sha512_valid(self):
        secret = "my-secret"
        payload = b"body"
        sig = compute_hmac(payload, secret, Algorithm.SHA512)
        v = WebhookSignatureVerifier(secret, Algorithm.SHA512)
        result = v.verify(payload, f"sha512={sig}")
        assert result.result == VerifyResult.VALID


class TestReplayProtection:
    def test_valid_timestamp(self):
        secret = "secret"
        now = time.time()
        ts = int(now)
        payload = b"data"
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        v = WebhookSignatureVerifier(secret)
        result = v.verify(payload, f"t={ts},v1={sig}", timestamp=ts, now=now)
        assert result.result == VerifyResult.VALID
        assert result.timestamp_age_seconds is not None
        assert result.timestamp_age_seconds < 5

    def test_expired_timestamp(self):
        secret = "secret"
        now = time.time()
        ts = int(now - 600)  # 10 minutes ago
        payload = b"data"
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        v = WebhookSignatureVerifier(secret, tolerance_seconds=300)
        result = v.verify(payload, f"t={ts},v1={sig}", timestamp=ts, now=now)
        assert result.result == VerifyResult.EXPIRED_TIMESTAMP

    def test_future_timestamp_rejected(self):
        secret = "secret"
        now = time.time()
        ts = int(now + 600)  # 10 minutes in future
        payload = b"data"
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        v = WebhookSignatureVerifier(secret, tolerance_seconds=300)
        result = v.verify(payload, f"t={ts},v1={sig}", timestamp=ts, now=now)
        assert result.result == VerifyResult.EXPIRED_TIMESTAMP

    def test_custom_tolerance(self):
        secret = "secret"
        now = time.time()
        ts = int(now - 50)  # 50 seconds ago
        payload = b"data"
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        # 60s tolerance → should pass
        v = WebhookSignatureVerifier(secret, tolerance_seconds=60)
        result = v.verify(payload, f"t={ts},v1={sig}", timestamp=ts, now=now)
        assert result.result == VerifyResult.VALID


class TestGitHubStyle:
    def test_github_verify(self):
        secret = "gh-webhook-secret"
        payload = b'{"action":"push"}'
        sig = compute_hmac(payload, secret)
        v = WebhookSignatureVerifier(secret)
        result = v.verify_github(payload, f"sha256={sig}")
        assert result.result == VerifyResult.VALID
        assert result.algorithm == "sha256"


class TestStripeStyle:
    def test_stripe_verify(self):
        secret = "whsec_stripe"
        now = time.time()
        ts = int(now)
        payload = b'{"type":"charge.succeeded"}'
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        v = WebhookSignatureVerifier(secret)
        result = v.verify_stripe(payload, f"t={ts},v1={sig}", now=now)
        assert result.result == VerifyResult.VALID

    def test_stripe_expired(self):
        secret = "whsec_stripe"
        now = time.time()
        ts = int(now - 600)
        payload = b'{"type":"charge.succeeded"}'
        signed = compute_signed_payload(ts, payload)
        sig = compute_hmac(signed, secret)
        v = WebhookSignatureVerifier(secret)
        result = v.verify_stripe(payload, f"t={ts},v1={sig}", now=now)
        assert result.result == VerifyResult.EXPIRED_TIMESTAMP


class TestAuditLog:
    def test_log_records_verification(self):
        v = WebhookSignatureVerifier("secret")
        v.verify(b"data", "sha256=wrong")
        v.verify(b"data", "sha256=wrong")
        log_entries = v.get_audit_log()
        assert len(log_entries) == 2
        assert all(e.result == VerifyResult.INVALID_SIGNATURE for e in log_entries)

    def test_log_limit(self):
        v = WebhookSignatureVerifier("secret")
        for _ in range(10):
            v.verify(b"data", "sha256=wrong")
        assert len(v.get_audit_log(limit=3)) == 3

    def test_log_records_source(self):
        v = WebhookSignatureVerifier("secret")
        v.verify(b"data", "sha256=wrong", source="stripe")
        log_entries = v.get_audit_log()
        assert log_entries[0].source == "stripe"
