"""Advanced webhook verification tests."""

from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature


def test_sign_deterministic():
    sig1 = sign_payload(b"test", "secret")
    sig2 = sign_payload(b"test", "secret")
    assert sig1 == sig2


def test_sign_different_payloads():
    sig1 = sign_payload(b"payload1", "secret")
    sig2 = sign_payload(b"payload2", "secret")
    assert sig1 != sig2


def test_sign_different_secrets():
    sig1 = sign_payload(b"test", "secret1")
    sig2 = sign_payload(b"test", "secret2")
    assert sig1 != sig2


def test_verify_correct():
    sig = sign_payload(b"hello", "mysecret")
    assert verify_signature(b"hello", sig, "mysecret")


def test_verify_wrong_payload():
    sig = sign_payload(b"hello", "mysecret")
    assert not verify_signature(b"wrong", sig, "mysecret")


def test_verify_wrong_secret():
    sig = sign_payload(b"hello", "mysecret")
    assert not verify_signature(b"hello", sig, "wrongsecret")


def test_verify_no_prefix():
    assert not verify_signature(b"test", "notsha256=xxx", "secret")


def test_secret_format():
    raw, hashed = generate_webhook_secret()
    assert raw.startswith("whsec_")
    assert len(hashed) == 64


def test_unicode_payload():
    payload = "你好世界".encode("utf-8")
    sig = sign_payload(payload, "secret")
    assert verify_signature(payload, sig, "secret")


def test_large_payload():
    payload = b"x" * 1_000_000
    sig = sign_payload(payload, "secret")
    assert verify_signature(payload, sig, "secret")
