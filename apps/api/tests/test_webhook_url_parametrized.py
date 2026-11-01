"""Parametrized webhook URL validation tests."""

import pytest
from app.services.app_webhooks import validate_webhook_url

VALID_URLS = [
    "https://hooks.slack.com/services/xxx",
    "https://api.example.com/webhook",
    "https://myapp.com/api/openskill/callback",
]

INVALID_URLS = [
    ("", "empty"),
    ("http://example.com/hook", "http"),
    ("ftp://x.com/hook", "ftp"),
    ("example.com/hook", "no scheme"),
    ("https://x.com/" + "a" * 500, "too long"),
    ("https://localhost/hook", "localhost"),
    ("https://169.254.169.254/meta", "aws metadata"),
]

@pytest.mark.parametrize("url", VALID_URLS)
def test_valid_url(url):
    errors = validate_webhook_url(url)
    format_errors = [e for e in errors if "HTTPS" in e or "required" in e.lower() or "500" in e]
    assert format_errors == []

@pytest.mark.parametrize("url,desc", INVALID_URLS, ids=lambda x: x if isinstance(x, str) else "url")
def test_invalid_url(url, desc):
    errors = validate_webhook_url(url)
    assert len(errors) > 0, f"Expected errors for {desc}: {url}"
