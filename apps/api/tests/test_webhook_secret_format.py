"""Webhook secret format tests."""

import pytest
from app.services.webhook_verify import generate_webhook_secret

def test_secret_tuple_length():
    result = generate_webhook_secret()
    assert len(result) == 2

def test_display_secret_is_string():
    display, _ = generate_webhook_secret()
    assert isinstance(display, str)

def test_raw_secret_is_string():
    _, raw = generate_webhook_secret()
    assert isinstance(raw, str)

def test_secrets_differ():
    """Each call generates unique secrets."""
    secrets = {generate_webhook_secret()[1] for _ in range(10)}
    assert len(secrets) == 10

def test_secret_length_reasonable():
    _, raw = generate_webhook_secret()
    assert len(raw) >= 16  # At least 16 chars for security

def test_display_format():
    display, _ = generate_webhook_secret()
    assert len(display) >= 16
