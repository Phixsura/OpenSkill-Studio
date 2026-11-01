"""App webhooks service tests — URL format validation."""

import pytest
from app.services.app_webhooks import validate_webhook_url

# These will fail DNS/SSRF check in test env, so we only test format-level rejection
FORMAT_INVALID_URLS = [
    ("ftp://example.com/hook", "non-https scheme"),
    ("javascript:alert(1)", "js scheme"),
    ("", "empty"),
    ("not-a-url", "not a URL"),
    ("http://127.0.0.1/hook", "loopback"),
    ("http://localhost/hook", "localhost"),
    ("https://[::1]/hook", "ipv6 loopback"),
]

@pytest.mark.parametrize("url,desc", FORMAT_INVALID_URLS, ids=lambda x: str(x)[:30])
def test_invalid_webhook_urls(url, desc):
    errors = validate_webhook_url(url)
    assert len(errors) > 0, f"Expected errors for {desc}: {url}"

def test_returns_list():
    result = validate_webhook_url("https://example.com")
    assert isinstance(result, list)

def test_multiple_issues():
    """A URL with multiple problems should report errors."""
    errors = validate_webhook_url("")
    assert len(errors) >= 1
