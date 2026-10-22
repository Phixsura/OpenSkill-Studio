"""Webhook URL validation format tests."""

import pytest
from app.services.app_webhooks import validate_webhook_url

HTTP_URLS = [
    "http://example.com/hook",
    "http://api.example.com:8080/webhook",
]

@pytest.mark.parametrize("url", HTTP_URLS)
def test_http_format_valid(url):
    errors = validate_webhook_url(url)
    # Should only have DNS/SSRF errors, not format errors
    format_errors = [e for e in errors if "format" in e.lower() or "scheme" in e.lower()]
    assert format_errors == []

CLEARLY_INVALID = [
    ("", "empty"),
    ("not-a-url", "no scheme"),
    ("ftp://x.com", "wrong scheme"),
]

@pytest.mark.parametrize("url,desc", CLEARLY_INVALID, ids=lambda x: str(x)[:20])
def test_clearly_invalid(url, desc):
    errors = validate_webhook_url(url)
    assert len(errors) > 0

def test_returns_list_type():
    assert isinstance(validate_webhook_url("https://x.com"), list)

def test_all_errors_are_strings():
    errors = validate_webhook_url("")
    for e in errors:
        assert isinstance(e, str)
