"""Tooltip — contextual help tooltips for marketplace UI elements."""

TOOLTIPS = {
    "install_count": {"text": "Total number of times this app has been installed across all organizations.", "learn_more": "/docs/metrics#installs"},
    "avg_rating": {"text": "Average rating from verified user reviews on a 1-5 scale.", "learn_more": "/docs/reviews"},
    "verified_developer": {"text": "This developer has verified their identity and domain ownership.", "learn_more": "/docs/verification"},
    "api_calls": {"text": "Number of API requests made by this app in the current billing period.", "learn_more": "/docs/quotas"},
    "webhook_delivery": {"text": "Percentage of webhooks successfully delivered to your endpoint.", "learn_more": "/docs/webhooks"},
    "error_rate": {"text": "Percentage of API requests that returned a 5xx error response.", "learn_more": "/docs/monitoring"},
    "uptime": {"text": "Percentage of time the app was available and responding in the last 30 days.", "learn_more": "/docs/sla"},
    "p99_latency": {"text": "99th percentile response time — 99% of requests complete faster than this.", "learn_more": "/docs/performance"},
}


def get_tooltip(*, key: str) -> dict | None:
    return TOOLTIPS.get(key)


def get_all_tooltips() -> dict:
    return TOOLTIPS
