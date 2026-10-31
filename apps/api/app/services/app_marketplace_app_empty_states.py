"""Empty states — user-friendly empty state messages for all marketplace views."""

EMPTY_STATES = {
    "no_apps": {"title": "No apps yet", "message": "Be the first to publish an app!", "icon": "📦", "action": "Create App", "action_url": "/developer/apps/new"},
    "no_reviews": {"title": "No reviews yet", "message": "Install and try this app, then leave a review.", "icon": "⭐", "action": "Install", "action_url": None},
    "no_installs": {"title": "No installations", "message": "Browse the marketplace to find useful apps.", "icon": "📥", "action": "Explore", "action_url": "/marketplace"},
    "no_webhooks": {"title": "No webhooks", "message": "Set up webhooks to receive real-time events.", "icon": "🔗", "action": "Add Webhook", "action_url": None},
    "no_results": {"title": "No results found", "message": "Try adjusting your search or filters.", "icon": "🔍", "action": "Clear Filters", "action_url": None},
    "no_notifications": {"title": "All caught up!", "message": "No new notifications.", "icon": "🎉", "action": None, "action_url": None},
}

def get_empty_state(*, state_type: str) -> dict:
    return EMPTY_STATES.get(state_type, {"title": "Nothing here", "message": "No content available.", "icon": "📭", "action": None, "action_url": None})
