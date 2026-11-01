"""App support contact — display developer support information."""
from __future__ import annotations
import html
from urllib.parse import urlparse


def build_support_info(app: dict) -> dict:
    support_url = app.get("support_url", "")
    docs_url = app.get("docs_url", "")
    return {
        "developer": html.escape(app.get("developer", "")),
        "support_email": app.get("support_email", ""),
        "support_url": support_url if _is_https(support_url) else "",
        "docs_url": docs_url if _is_https(docs_url) else "",
        "response_time": app.get("response_time", "24 hours"),
        "channels": _get_channels(app),
    }


def _is_https(url: str) -> bool:
    if not url:
        return False
    return urlparse(url).scheme == "https"


def _get_channels(app: dict) -> list[dict]:
    channels = []
    if app.get("support_email"):
        channels.append({"type": "email", "icon": "📧", "value": app["support_email"]})
    if app.get("support_url"):
        channels.append({"type": "web", "icon": "🌐", "value": "Support Portal"})
    if app.get("discord_url"):
        channels.append({"type": "discord", "icon": "💬", "value": "Discord Community"})
    return channels
