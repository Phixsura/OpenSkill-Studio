"""Webhook HMAC edge cases."""

import pytest
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

def test_empty_payload():
    _, secret = generate_webhook_secret()
    sig = sign_payload(b"", secret)
    assert verify_signature(b"", sig, secret)

def test_large_payload():
    payload = b"x" * 100_000
    _, secret = generate_webhook_secret()
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

def test_unicode_in_payload():
    payload = "héllo wörld 你好".encode("utf-8")
    _, secret = generate_webhook_secret()
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

def test_signature_is_deterministic():
    _, secret = generate_webhook_secret()
    sig1 = sign_payload(b"test", secret)
    sig2 = sign_payload(b"test", secret)
    assert sig1 == sig2

def test_different_payloads_different_sigs():
    _, secret = generate_webhook_secret()
    sig1 = sign_payload(b"payload1", secret)
    sig2 = sign_payload(b"payload2", secret)
    assert sig1 != sig2

def test_truncated_signature_fails():
    _, secret = generate_webhook_secret()
    sig = sign_payload(b"test", secret)
    assert not verify_signature(b"test", sig[:10], secret)

def test_empty_secret_still_works():
    """Even empty secret should produce valid HMAC."""
    sig = sign_payload(b"test", "")
    assert verify_signature(b"test", sig, "")
    assert not verify_signature(b"test", sig, "different")
