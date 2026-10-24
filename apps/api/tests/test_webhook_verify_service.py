"""Webhook verification — sign/verify round-trip."""

import pytest
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

PAYLOADS = [
    b'{"event":"test"}',
    b'{}',
    b'hello world',
    b'\x00\x01\x02',
    b'a' * 10000,
]

def test_generate_secret_returns_tuple():
    result = generate_webhook_secret()
    assert isinstance(result, tuple)
    assert len(result) == 2

def test_generate_secret_unique():
    a = generate_webhook_secret()
    b = generate_webhook_secret()
    assert a[0] != b[0]

@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: repr(p)[:30])
def test_sign_verify_roundtrip(payload):
    _, secret = generate_webhook_secret()
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

@pytest.mark.parametrize("payload", PAYLOADS, ids=lambda p: repr(p)[:30])
def test_wrong_secret_fails(payload):
    _, secret1 = generate_webhook_secret()
    _, secret2 = generate_webhook_secret()
    sig = sign_payload(payload, secret1)
    assert not verify_signature(payload, sig, secret2)

def test_tampered_payload_fails():
    _, secret = generate_webhook_secret()
    sig = sign_payload(b'original', secret)
    assert not verify_signature(b'tampered', sig, secret)

def test_signature_format():
    _, secret = generate_webhook_secret()
    sig = sign_payload(b'test', secret)
    assert isinstance(sig, str)
    assert len(sig) > 10
