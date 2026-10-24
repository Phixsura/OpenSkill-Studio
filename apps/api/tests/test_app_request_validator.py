"""App request validator tests."""
import pytest
from app.services.app_request_validator import validate_request, MAX_BODY_SIZE

def test_valid_request():
    r = validate_request(content_type="application/json", body_size=100, body=b'{"ok":true}')
    assert r["valid"] is True

def test_body_too_large():
    r = validate_request(body_size=MAX_BODY_SIZE + 1)
    assert r["valid"] is False
    assert any("too large" in e for e in r["errors"])

def test_bad_content_type():
    r = validate_request(content_type="text/xml")
    assert r["valid"] is False

def test_valid_content_types():
    for ct in ["application/json", "application/x-www-form-urlencoded"]:
        assert validate_request(content_type=ct)["valid"] is True

def test_missing_header():
    r = validate_request(required_headers={"X-Api-Key": "key123"}, actual_headers={})
    assert r["valid"] is False

def test_invalid_json():
    r = validate_request(content_type="application/json", body=b"not json", body_size=8)
    assert r["valid"] is False

def test_valid_json():
    r = validate_request(content_type="application/json", body=b'{"key":"val"}', body_size=14)
    assert r["valid"] is True

def test_empty_request():
    r = validate_request()
    assert r["valid"] is True
