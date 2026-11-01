"""Crypto and signing comprehensive tests."""

from app.services.developer import _generate_api_key, _generate_oauth_client_id, _generate_oauth_client_secret, _get_fernet
from app.services.webhook_verify import generate_webhook_secret, sign_payload, verify_signature


def test_api_key_prefix():
    _, prefix, _ = _generate_api_key()
    assert prefix.startswith("osk_app_")

def test_api_key_hash_length():
    _, _, h = _generate_api_key()
    assert len(h) == 64

def test_api_key_10_unique():
    keys = {_generate_api_key()[0] for _ in range(10)}
    assert len(keys) == 10

def test_oauth_id_prefix():
    assert _generate_oauth_client_id().startswith("osk_")

def test_oauth_secret_hash():
    raw, h = _generate_oauth_client_secret()
    assert len(h) == 64
    assert len(raw) > 20

def test_fernet_roundtrip():
    f = _get_fernet()
    plain = b"my secret data 123"
    enc = f.encrypt(plain)
    assert f.decrypt(enc) == plain

def test_fernet_different_each_time():
    f = _get_fernet()
    e1 = f.encrypt(b"same")
    e2 = f.encrypt(b"same")
    assert e1 != e2

def test_webhook_secret_prefix():
    raw, _ = generate_webhook_secret()
    assert raw.startswith("whsec_")

def test_webhook_sign_format():
    sig = sign_payload(b"data", "secret")
    assert sig.startswith("sha256=")

def test_webhook_verify_tampered():
    sig = sign_payload(b"orig", "secret")
    assert not verify_signature(b"tampered", sig, "secret")

def test_webhook_verify_wrong_secret():
    sig = sign_payload(b"data", "right")
    assert not verify_signature(b"data", sig, "wrong")

def test_webhook_verify_correct():
    sig = sign_payload(b"data", "key")
    assert verify_signature(b"data", sig, "key")

def test_webhook_unicode():
    data = "中文测试".encode()
    sig = sign_payload(data, "key")
    assert verify_signature(data, sig, "key")

def test_webhook_empty():
    sig = sign_payload(b"", "key")
    assert verify_signature(b"", sig, "key")
