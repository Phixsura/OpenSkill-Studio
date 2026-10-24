"""Webhook configuration builder — prepare webhook config for installations."""


def build_webhook_config(
    *,
    webhook_url: str,
    events: list[str],
    secret: str,
    active: bool = True,
    max_retries: int = 5,
) -> dict:
    """Build a complete webhook configuration."""
    return {
        "url": webhook_url,
        "events": sorted(events),
        "secret": secret,
        "active": active,
        "max_retries": max_retries,
        "content_type": "application/json",
        "ssl_verification": True,
    }


def validate_webhook_config(config: dict) -> list[str]:
    """Validate a webhook configuration."""
    errors = []
    if not config.get("url"):
        errors.append("Webhook URL is required")
    if not config.get("events"):
        errors.append("At least one event is required")
    if not config.get("secret"):
        errors.append("Webhook secret is required")
    if config.get("max_retries", 0) > 10:
        errors.append("Max retries cannot exceed 10")
    return errors
