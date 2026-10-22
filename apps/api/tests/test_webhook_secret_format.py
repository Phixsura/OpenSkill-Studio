"""Parametrized webhook secret generation format tests."""

import pytest
from app.services.webhook_verify import generate_webhook_secret

@pytest.mark.parametrize("_", range(20))
def test_secret_prefix(_):
    raw, _ = generate_webhook_secret()
    assert raw.startswith("whsec_")

@pytest.mark.parametrize("_", range(20))
def test_hash_length(_):
    _, h = generate_webhook_secret()
    assert len(h) == 64

def test_all_unique():
    secrets = {generate_webhook_secret()[0] for _ in range(50)}
    assert len(secrets) == 50
