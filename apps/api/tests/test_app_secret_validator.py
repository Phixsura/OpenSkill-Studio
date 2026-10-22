"""Secret validator tests."""
import pytest
from app.services.app_secret_validator import validate_secret_key, validate_secret_value

VALID_KEYS = ["API_KEY", "LMS_TOKEN", "OAUTH_CLIENT_SECRET", "DB_HOST"]

@pytest.mark.parametrize("key", VALID_KEYS)
def test_valid_key(key):
    assert validate_secret_key(key) == []

INVALID_KEYS = ["", "lowercase", "has space", "1STARTS_WITH_NUM", "a"]

@pytest.mark.parametrize("key", INVALID_KEYS)
def test_invalid_key(key):
    assert len(validate_secret_key(key)) > 0

def test_generic_key_rejected():
    assert len(validate_secret_key("PASSWORD")) > 0

def test_valid_value():
    assert validate_secret_value("my-secret-value") == []

def test_empty_value():
    assert len(validate_secret_value("")) > 0

def test_too_long_value():
    assert len(validate_secret_value("x" * 20000)) > 0
