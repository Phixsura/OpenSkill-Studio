"""Parametrized API key format tests."""

import pytest
from app.services.developer import _generate_api_key, _generate_oauth_client_id, _generate_oauth_client_secret

@pytest.mark.parametrize("_", range(10))
def test_api_key_format(_):
    full, prefix, h = _generate_api_key()
    assert full.startswith("osk_app_")
    assert prefix == full[:12]
    assert len(h) == 64

@pytest.mark.parametrize("_", range(10))
def test_oauth_id_format(_):
    cid = _generate_oauth_client_id()
    assert cid.startswith("osk_")
    assert len(cid) > 20

@pytest.mark.parametrize("_", range(5))
def test_oauth_secret_format(_):
    raw, h = _generate_oauth_client_secret()
    assert len(raw) > 20
    assert len(h) == 64
