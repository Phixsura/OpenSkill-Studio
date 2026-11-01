"""CORS config tests."""
import pytest
from app.services.app_cors_config import build_cors_origins, is_origin_allowed

def test_extract_origins():
    uris = ["https://app.example.com/callback", "https://app.example.com/auth"]
    origins = build_cors_origins(uris)
    assert origins == ["https://app.example.com"]

def test_multiple_origins():
    uris = ["https://a.com/cb", "https://b.com/cb"]
    assert len(build_cors_origins(uris)) == 2

def test_port_included():
    origins = build_cors_origins(["http://localhost:3000/cb"])
    assert "http://localhost:3000" in origins

def test_standard_port_excluded():
    origins = build_cors_origins(["https://app.com:443/cb"])
    assert "https://app.com" in origins

def test_is_allowed():
    assert is_origin_allowed("https://app.com", ["https://app.com"]) is True
    assert is_origin_allowed("https://evil.com", ["https://app.com"]) is False
