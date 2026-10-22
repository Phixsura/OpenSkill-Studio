"""App signing utility tests."""

import pytest
from app.services.app_signing import sign_content, verify_content, sign_manifest, verify_manifest, generate_fingerprint

def test_sign_verify_roundtrip():
    sig = sign_content(b"hello", "key")
    assert verify_content(b"hello", sig, "key")

def test_wrong_key_fails():
    sig = sign_content(b"hello", "key1")
    assert not verify_content(b"hello", sig, "key2")

def test_tampered_content_fails():
    sig = sign_content(b"hello", "key")
    assert not verify_content(b"tampered", sig, "key")

def test_manifest_sign_verify():
    m = {"app": {"name": "Test"}, "version": "1.0.0"}
    sig = sign_manifest(m, "secret")
    assert verify_manifest(m, sig, "secret")

def test_manifest_order_independent():
    m1 = {"b": 2, "a": 1}
    m2 = {"a": 1, "b": 2}
    assert sign_manifest(m1, "k") == sign_manifest(m2, "k")

def test_fingerprint_format():
    fp = generate_fingerprint("ssh-rsa AAAA...")
    assert len(fp) == 32

def test_fingerprint_deterministic():
    assert generate_fingerprint("key") == generate_fingerprint("key")

def test_fingerprint_unique():
    assert generate_fingerprint("key1") != generate_fingerprint("key2")
