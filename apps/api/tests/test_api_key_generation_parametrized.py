"""Parametrized API key generation tests."""

import pytest
from app.services.developer import _generate_api_key

@pytest.mark.parametrize("_", range(20))
def test_key_starts_with_osk_app(_):
    full, _, _ = _generate_api_key()
    assert full.startswith("osk_app_")

@pytest.mark.parametrize("_", range(20))
def test_prefix_matches(_):
    full, prefix, _ = _generate_api_key()
    assert full[:12] == prefix

@pytest.mark.parametrize("_", range(20))
def test_hash_is_64_hex(_):
    _, _, h = _generate_api_key()
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

def test_all_keys_unique():
    keys = {_generate_api_key()[0] for _ in range(50)}
    assert len(keys) == 50
