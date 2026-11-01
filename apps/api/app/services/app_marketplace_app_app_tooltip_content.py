"""Tooltip content — contextual help tooltips for UI elements."""


TOOLTIPS = {
    "api_key": {"title": "API Key", "content": "Your secret key for authenticating API requests. Never share this publicly.",
                "link": "/docs/authentication", "category": "security"},
    "webhook_url": {"title": "Webhook URL", "content": "The endpoint where we'll send event notifications.",
                     "link": "/docs/webhooks", "category": "integration"},
    "rate_limit": {"title": "Rate Limit", "content": "Maximum number of API requests per minute. Upgrade for higher limits.",
                    "link": "/pricing", "category": "usage"},
    "sandbox": {"title": "Sandbox Mode", "content": "Test your app safely without affecting production data.",
                 "link": "/docs/sandbox", "category": "development"},
    "version": {"title": "App Version", "content": "Semantic version (major.minor.patch). Major versions may have breaking changes.",
                 "link": "/docs/versioning", "category": "release"},
}


def get_tooltip(*, tooltip_id: str) -> dict:
    tip = TOOLTIPS.get(tooltip_id)
    if not tip:
        return {"error": f"Unknown tooltip: {tooltip_id}"}
    return {"id": tooltip_id, **tip}


def get_tooltips_by_category(*, category: str) -> dict:
    filtered = {k: v for k, v in TOOLTIPS.items() if v["category"] == category}
    return {"category": category, "tooltips": [{"id": k, **v} for k, v in filtered.items()],
            "count": len(filtered)}
