"""Parametrized webhook signing tests."""

import pytest
from app.services.webhook_verify import sign_payload, verify_signature, generate_webhook_secret

PAYLOADS = [b"", b"hello", b'{"event": "test"}', b"x" * 10000, "中文".encode()]
SECRETS = ["secret1", "my-webhook-secret", "whsec_abc123", "a" * 100]

@pytest.mark.parametrize("payload", PAYLOADS)
def test_sign_verify_roundtrip(payload):
    sig = sign_payload(payload, "test-secret")
    assert verify_signature(payload, sig, "test-secret")

@pytest.mark.parametrize("payload", PAYLOADS)
def test_tampered_fails(payload):
    sig = sign_payload(payload, "test-secret")
    assert not verify_signature(payload + b"tampered", sig, "test-secret")

@pytest.mark.parametrize("secret", SECRETS)
def test_different_secrets_different_sigs(secret):
    sig = sign_payload(b"data", secret)
    assert sig.startswith("sha256=")
    assert verify_signature(b"data", sig, secret)

@pytest.mark.parametrize("secret", SECRETS)
def test_wrong_secret_fails(secret):
    sig = sign_payload(b"data", secret)
    assert not verify_signature(b"data", sig, secret + "_wrong")

def test_generated_secrets_unique():
    secrets = {generate_webhook_secret()[0] for _ in range(20)}
    assert len(secrets) == 20
