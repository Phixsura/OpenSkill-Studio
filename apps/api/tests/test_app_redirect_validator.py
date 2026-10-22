"""Redirect URI validator tests."""
import pytest
from app.services.app_redirect_validator import validate_redirect_uri

REGISTERED = ["https://app.com/callback", "http://localhost:3000/auth"]

def test_valid():
    assert validate_redirect_uri("https://app.com/callback", REGISTERED)["valid"] is True

def test_not_registered():
    assert validate_redirect_uri("https://evil.com/cb", REGISTERED)["valid"] is False

def test_empty():
    assert validate_redirect_uri("", REGISTERED)["valid"] is False

def test_localhost_registered():
    assert validate_redirect_uri("http://localhost:3000/auth", REGISTERED)["valid"] is True

def test_unregistered_localhost():
    assert validate_redirect_uri("http://localhost:4000/auth", REGISTERED)["valid"] is False
