"""App content hash tests."""

import pytest
from app.services.app_content_hash import (
    hash_manifest, hash_content, hash_files, verify_content_hash, generate_version_hash,
)

def test_hash_manifest_deterministic():
    m = {"b": 2, "a": 1}
    assert hash_manifest(m) == hash_manifest({"a": 1, "b": 2})

def test_hash_manifest_length():
    h = hash_manifest({"test": True})
    assert len(h) == 64

def test_hash_content():
    h = hash_content(b"hello world")
    assert len(h) == 64

def test_hash_content_deterministic():
    assert hash_content(b"test") == hash_content(b"test")

def test_hash_content_different():
    assert hash_content(b"a") != hash_content(b"b")

def test_hash_files_deterministic():
    files = {"a.js": b"console.log(1)", "b.js": b"console.log(2)"}
    assert hash_files(files) == hash_files(files)

def test_hash_files_order_independent():
    f1 = {"b.js": b"2", "a.js": b"1"}
    f2 = {"a.js": b"1", "b.js": b"2"}
    assert hash_files(f1) == hash_files(f2)

def test_hash_files_content_sensitive():
    f1 = {"a.js": b"1"}
    f2 = {"a.js": b"2"}
    assert hash_files(f1) != hash_files(f2)

def test_verify_content_hash():
    m = {"schema_version": "1.0", "app": {"name": "Test"}}
    h = hash_manifest(m)
    assert verify_content_hash(m, h) is True
    assert verify_content_hash(m, "wrong") is False

def test_generate_version_hash():
    m = {"app": {"name": "Test"}}
    h = generate_version_hash(manifest=m)
    assert len(h) == 64

def test_generate_version_hash_with_source():
    m = {"app": {"name": "Test"}}
    h1 = generate_version_hash(manifest=m)
    h2 = generate_version_hash(manifest=m, source_hash="abc123")
    assert h1 != h2
