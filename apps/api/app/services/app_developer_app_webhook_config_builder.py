"""Webhook config page builder — compile webhook settings for app detail."""


def build_webhook_config_page(*, app: dict, webhook_url: str | None, secret_configured: bool,
                                 subscriptions: list[dict], delivery_stats: dict) -> dict:
    return {
        "app_name": app.get("name"),
        "webhook_url": webhook_url,
        "is_configured": bool(webhook_url),
        "secret_configured": secret_configured,
        "subscriptions": subscriptions,
        "subscription_count": len(subscriptions),
        "delivery_stats": delivery_stats,
        "setup_complete": bool(webhook_url) and secret_configured and len(subscriptions) > 0,
    }
