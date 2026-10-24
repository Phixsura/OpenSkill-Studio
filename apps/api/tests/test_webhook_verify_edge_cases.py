"""Webhook verify — additional edge cases."""

import pytest
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature

def test_binary_payload():
    _, secret = generate_webhook_secret()
    payload = bytes(range(256))
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

def test_json_payload():
    import json
    _, secret = generate_webhook_secret()
    data = {"event": "test", "data": {"nested": [1, 2, 3]}, "unicode": "你好"}
    payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
    sig = sign_payload(payload, secret)
    assert verify_signature(payload, sig, secret)

def test_signature_not_empty():
    _, secret = generate_webhook_secret()
    sig = sign_payload(b"test", secret)
    assert len(sig) > 0

def test_different_secrets_different_sigs():
    _, s1 = generate_webhook_secret()
    _, s2 = generate_webhook_secret()
    sig1 = sign_payload(b"same", s1)
    sig2 = sign_payload(b"same", s2)
    assert sig1 != sig2

def test_100_unique_secrets():
    secrets = set()
    for _ in range(100):
        _, s = generate_webhook_secret()
        secrets.add(s)
    assert len(secrets) == 100

def test_sign_verify_consistency_many():
    _, secret = generate_webhook_secret()
    for i in range(50):
        payload = f"payload-{i}".encode()
        sig = sign_payload(payload, secret)
        assert verify_signature(payload, sig, secret)
        assert not verify_signature(f"wrong-{i}".encode(), sig, secret)
