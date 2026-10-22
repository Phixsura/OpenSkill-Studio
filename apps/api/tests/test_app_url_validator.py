"""URL validator tests."""
import pytest
from app.services.app_url_validator import validate_url, is_safe_redirect_uri

def test_valid_https():
    assert validate_url("https://example.com") == []

def test_valid_http():
    assert validate_url("http://example.com") == []

def test_require_https_rejects_http():
    errors = validate_url("http://example.com", require_https=True)
    assert len(errors) > 0

def test_ftp_rejected():
    assert len(validate_url("ftp://x.com")) > 0

def test_localhost_blocked():
    assert len(validate_url("http://localhost/x")) > 0

def test_loopback_blocked():
    assert len(validate_url("http://127.0.0.1/x")) > 0

def test_internal_blocked():
    assert len(validate_url("http://app.internal/x")) > 0

def test_empty():
    assert len(validate_url("")) > 0

def test_safe_redirect():
    assert is_safe_redirect_uri("https://app.example.com/callback") is True

def test_unsafe_redirect():
    assert is_safe_redirect_uri("http://app.example.com/callback") is False
