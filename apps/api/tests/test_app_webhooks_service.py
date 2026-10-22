"""App webhooks service tests."""

import pytest
from app.services.app_webhooks import validate_webhook_url

VALID_URLS = [
    "https://example.com/webhook",
    "https://api.myapp.io/hooks/event",
    "https://hooks.slack.com/services/T00/B00/xxx",
]

INVALID_URLS = [
    "http://localhost/hook",
    "http://127.0.0.1/hook",
    "ftp://example.com/hook",
    "javascript:alert(1)",
    "",
    "not-a-url",
]

@pytest.mark.parametrize("url", VALID_URLS)
def test_valid_webhook_urls(url):
    errors = validate_webhook_url(url)
    assert errors == [], f"Unexpected errors for {url}: {errors}"

@pytest.mark.parametrize("url", INVALID_URLS)
def test_invalid_webhook_urls(url):
    errors = validate_webhook_url(url)
    assert len(errors) > 0, f"Expected errors for {url}"
