"""Tests to hit 700 milestone — final coverage gaps."""

from app.services.app_webhooks import generate_webhook_secret, validate_webhook_url
from app.services.app_metrics import record_event_dispatch, get_all_counts


def test_webhook_url_valid_https():
    errors = validate_webhook_url("https://hooks.slack.com/services/T00/B00/xxx")
    format_errors = [e for e in errors if "HTTPS" in e or "required" in e.lower()]
    assert format_errors == []


def test_webhook_url_rejects_ftp():
    errors = validate_webhook_url("ftp://evil.com/hook")
    assert any("HTTPS" in e for e in errors)


def test_event_dispatch_metric():
    record_event_dispatch("app-700")
    counts = get_all_counts("app-700")
    assert counts.get("event_dispatches", 0) >= 1
