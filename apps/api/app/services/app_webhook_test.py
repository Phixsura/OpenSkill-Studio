"""Webhook test sender — send test events to webhook URLs."""

from app.services.app_url_validator import validate_url


def build_test_event(event_type: str = "test.ping") -> dict:
    return {"event_type": event_type, "data": {"test": True, "message": "This is a test webhook delivery"}, "test": True}


def validate_test_target(url: str) -> list[str]:
    """Validate test webhook target with SSRF protection."""
    return validate_url(url, label="Test webhook URL")
