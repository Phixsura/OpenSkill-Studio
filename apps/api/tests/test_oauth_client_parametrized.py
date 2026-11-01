"""Parametrized OAuth client ID generation tests."""

import pytest
from app.services.developer import _generate_oauth_client_id, _generate_oauth_client_secret

@pytest.mark.parametrize("_", range(20))
def test_client_id_prefix(_):
    assert _generate_oauth_client_id().startswith("osk_")

@pytest.mark.parametrize("_", range(10))
def test_client_id_length(_):
    assert len(_generate_oauth_client_id()) > 20

@pytest.mark.parametrize("_", range(10))
def test_client_secret_hash_length(_):
    _, h = _generate_oauth_client_secret()
    assert len(h) == 64

def test_all_client_ids_unique():
    ids = {_generate_oauth_client_id() for _ in range(30)}
    assert len(ids) == 30

def test_all_secrets_unique():
    secrets = {_generate_oauth_client_secret()[0] for _ in range(30)}
    assert len(secrets) == 30
