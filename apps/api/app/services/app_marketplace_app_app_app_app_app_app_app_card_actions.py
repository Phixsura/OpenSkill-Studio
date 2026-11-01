"""App card actions — contextual actions for marketplace app cards."""
from __future__ import annotations


def get_card_actions(*, installed: bool, owned: bool, favorited: bool) -> list[dict]:
    actions = []
    if not installed:
        actions.append({"id": "install", "label": "Install", "icon": "📥", "variant": "primary"})
    else:
        actions.append({"id": "open", "label": "Open", "icon": "🔗", "variant": "primary"})
        actions.append({"id": "uninstall", "label": "Uninstall", "icon": "🗑️", "variant": "danger"})
    actions.append({"id": "favorite", "label": "Unfavorite" if favorited else "Favorite",
                      "icon": "❤️" if favorited else "🤍", "variant": "secondary"})
    actions.append({"id": "share", "label": "Share", "icon": "📤", "variant": "secondary"})
    if owned:
        actions.append({"id": "edit", "label": "Edit Listing", "icon": "✏️", "variant": "secondary"})
        actions.append({"id": "analytics", "label": "Analytics", "icon": "📊", "variant": "secondary"})
    return actions


def get_quick_actions(app_status: str) -> list[dict]:
    if app_status == "draft":
        return [{"id": "publish", "label": "Submit for Review", "icon": "📤"}]
    if app_status == "in_review":
        return [{"id": "withdraw", "label": "Withdraw", "icon": "↩️"}]
    if app_status == "published":
        return [{"id": "update", "label": "Push Update", "icon": "🔄"},
                {"id": "suspend", "label": "Suspend", "icon": "⏸️"}]
    return []
