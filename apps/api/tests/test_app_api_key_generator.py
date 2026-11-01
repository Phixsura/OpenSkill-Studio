"""API key generator tests."""

import pytest
from app.services.app_api_key_generator import (
    generate_api_key, hash_api_key, verify_api_key, is_valid_key_format, PREFIX,
)

def test_generate_returns_triple():
    raw, prefix, hash_ = generate_api_key()
    assert isinstance(raw, str)
    assert isinstance(prefix, str)
    assert isinstance(hash_, str)

def test_raw_key_has_prefix():
    raw, _, _ = generate_api_key()
    assert raw.startswith(PREFIX)

def test_prefix_matches():
    raw, prefix, _ = generate_api_key()
    assert raw.startswith(prefix)

def test_hash_is_sha256():
    _, _, hash_ = generate_api_key()
    assert len(hash_) == 64

def test_unique_keys():
    keys = {generate_api_key()[0] for _ in range(50)}
    assert len(keys) == 50

def test_verify_correct():
    raw, _, hash_ = generate_api_key()
    assert verify_api_key(raw, hash_) is True

def test_verify_wrong():
    raw, _, _ = generate_api_key()
    assert verify_api_key(raw, "0" * 64) is False

def test_hash_deterministic():
    assert hash_api_key("test") == hash_api_key("test")

def test_is_valid_format():
    raw, _, _ = generate_api_key()
    assert is_valid_key_format(raw) is True

def test_invalid_format():
    assert is_valid_key_format("short") is False
    assert is_valid_key_format("wrong_prefix_abcdefghij") is False
