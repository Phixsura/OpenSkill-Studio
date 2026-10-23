"""API changelog subscription — notify developers of API changes."""
from __future__ import annotations
import html


def create_subscription(*, email: str, api_versions: list[str],
                          notify_breaking: bool = True,
                          notify_deprecations: bool = True,
                          notify_new: bool = False) -> dict:
    return {
        "email": email, "api_versions": api_versions,
        "preferences": {"breaking": notify_breaking, "deprecations": notify_deprecations, "new": notify_new},
        "active": True,
    }


def match_notification(change: dict, subscription: dict) -> bool:
    prefs = subscription["preferences"]
    change_type = change.get("type", "")
    if change_type == "breaking" and prefs.get("breaking"):
        return True
    if change_type == "deprecation" and prefs.get("deprecations"):
        return True
    if change_type == "new" and prefs.get("new"):
        return True
    return False


def build_notification(changes: list[dict], subscription: dict) -> dict:
    matched = [c for c in changes if match_notification(c, subscription)]
    return {
        "email": subscription["email"],
        "changes": [{"type": c["type"], "title": html.escape(c.get("title", "")),
                       "version": c.get("version", "")} for c in matched],
        "count": len(matched), "should_send": len(matched) > 0,
    }
