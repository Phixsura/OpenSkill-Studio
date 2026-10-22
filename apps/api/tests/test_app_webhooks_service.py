"""Tests for app webhook management service."""

from app.services.app_webhooks import generate_webhook_secret, validate_webhook_url


def test_generate_webhook_secret():
    raw, hashed = generate_webhook_secret()
    assert raw.startswith("whsec_")
    assert len(hashed) == 64
    # Each call unique
    raw2, _ = generate_webhook_secret()
    assert raw != raw2


def test_validate_webhook_url_https_format():
    """HTTPS URLs pass the format check (SSRF check may vary by network)."""
    errors = validate_webhook_url("https://api.github.com/webhook")
    # Should at minimum not have format errors
    format_errors = [e for e in errors if "HTTPS" in e or "required" in e.lower() or "500" in e]
    assert format_errors == []


def test_validate_webhook_url_empty():
    errors = validate_webhook_url("")
    assert len(errors) >= 1
    assert "required" in errors[0].lower()


def test_validate_webhook_url_http():
    errors = validate_webhook_url("http://example.com/webhook")
    assert any("HTTPS" in e for e in errors)


def test_validate_webhook_url_too_long():
    errors = validate_webhook_url("https://example.com/" + "x" * 500)
    assert any("500" in e for e in errors)


def test_validate_webhook_url_localhost():
    errors = validate_webhook_url("https://localhost/webhook")
    assert any("blocked" in e.lower() or "private" in e.lower() for e in errors)


def test_validate_webhook_url_metadata():
    errors = validate_webhook_url("https://169.254.169.254/latest/meta-data")
    assert any("blocked" in e.lower() or "private" in e.lower() for e in errors)
