"""Parametrized Fernet encryption tests."""

import pytest
from app.services.developer import _get_fernet

PLAINTEXTS = [
    b"simple",
    b"api_key_123456789",
    b"",
    b"x" * 1000,
    "中文密码".encode(),
    b'{"key": "value"}',
    b"\x00\x01\x02\x03",
]

@pytest.mark.parametrize("plaintext", PLAINTEXTS)
def test_encrypt_decrypt_roundtrip(plaintext):
    f = _get_fernet()
    encrypted = f.encrypt(plaintext)
    assert f.decrypt(encrypted) == plaintext
    assert encrypted != plaintext

@pytest.mark.parametrize("plaintext", PLAINTEXTS)
def test_different_ciphertexts(plaintext):
    f = _get_fernet()
    e1 = f.encrypt(plaintext)
    e2 = f.encrypt(plaintext)
    assert e1 != e2  # Random IV

def test_fernet_singleton():
    f1 = _get_fernet()
    f2 = _get_fernet()
    # Both should work
    enc = f1.encrypt(b"test")
    assert f2.decrypt(enc) == b"test"
