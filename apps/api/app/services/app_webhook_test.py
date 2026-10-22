"""Webhook test sender — send test events to webhook URLs."""

def build_test_event(event_type: str = "test.ping") -> dict:
    return {"event_type": event_type, "data": {"test": True, "message": "This is a test webhook delivery"}, "test": True}

def validate_test_target(url: str) -> list[str]:
    errors = []
    if not url: errors.append("URL required")
    elif not url.startswith(("http://", "https://")): errors.append("Must be HTTP(S)")
    return errors
