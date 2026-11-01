"""Comprehensive webhook URL validation tests."""

from app.services.app_webhooks import validate_webhook_url


def test_valid_https():
    errors = validate_webhook_url("https://api.example.com/webhook")
    format_errs = [e for e in errors if "HTTPS" in e or "required" in e.lower() or "500" in e]
    assert format_errs == []

def test_http_rejected():
    assert any("HTTPS" in e for e in validate_webhook_url("http://example.com/hook"))

def test_empty_rejected():
    assert any("required" in e.lower() for e in validate_webhook_url(""))

def test_too_long_rejected():
    assert any("500" in e for e in validate_webhook_url("https://x.com/" + "a" * 500))

def test_localhost_blocked():
    errors = validate_webhook_url("https://localhost/hook")
    assert any("blocked" in e.lower() or "private" in e.lower() for e in errors)

def test_metadata_blocked():
    errors = validate_webhook_url("https://169.254.169.254/meta")
    assert any("blocked" in e.lower() or "private" in e.lower() for e in errors)

def test_ftp_rejected():
    assert any("HTTPS" in e for e in validate_webhook_url("ftp://x.com/hook"))

def test_no_scheme_rejected():
    errors = validate_webhook_url("example.com/hook")
    assert len(errors) > 0
