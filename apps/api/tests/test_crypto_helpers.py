"""Tests for crypto helpers — key generation, hashing."""

from app.services.developer import _generate_api_key, _generate_oauth_client_id, _generate_oauth_client_secret


def test_api_key_format():
    full, prefix, h = _generate_api_key()
    assert full.startswith("osk_app_")
    assert prefix == full[:12]
    assert len(h) == 64  # SHA-256 hex


def test_api_key_uniqueness():
    keys = [_generate_api_key()[0] for _ in range(10)]
    assert len(set(keys)) == 10


def test_oauth_client_id_format():
    cid = _generate_oauth_client_id()
    assert cid.startswith("osk_")
    assert len(cid) > 20


def test_oauth_client_id_uniqueness():
    ids = [_generate_oauth_client_id() for _ in range(10)]
    assert len(set(ids)) == 10


def test_oauth_client_secret():
    raw, hashed = _generate_oauth_client_secret()
    assert len(raw) > 20
    assert len(hashed) == 64
    # Different calls = different secrets
    raw2, _ = _generate_oauth_client_secret()
    assert raw != raw2


def test_fernet_key_generation():
    from app.services.developer import _get_fernet
    f = _get_fernet()
    # Encrypt and decrypt roundtrip
    plaintext = b"test secret value"
    encrypted = f.encrypt(plaintext)
    assert f.decrypt(encrypted) == plaintext


def test_fernet_different_encryptions():
    from app.services.developer import _get_fernet
    f = _get_fernet()
    e1 = f.encrypt(b"test")
    e2 = f.encrypt(b"test")
    assert e1 != e2  # Fernet uses random IV
