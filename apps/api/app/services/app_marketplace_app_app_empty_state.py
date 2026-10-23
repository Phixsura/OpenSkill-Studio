"""Empty state — contextual empty state content for different pages."""

import html

EMPTY_STATES = {
    "apps": {"icon": "📦", "title": "No apps yet", "description": "Create your first app to get started.",
             "cta_label": "Create App", "cta_action": "/apps/new"},
    "webhooks": {"icon": "🔗", "title": "No webhooks configured", "description": "Set up webhooks to receive real-time events.",
                  "cta_label": "Add Webhook", "cta_action": "/webhooks/new"},
    "reviews": {"icon": "⭐", "title": "No reviews yet", "description": "Reviews will appear here once users rate your app.",
                 "cta_label": None, "cta_action": None},
    "search": {"icon": "🔍", "title": "No results found", "description": "Try a different search term or broaden your filters.",
                "cta_label": "Clear Filters", "cta_action": "clear"},
    "notifications": {"icon": "🔔", "title": "All caught up!", "description": "You have no new notifications.",
                       "cta_label": None, "cta_action": None},
}


def get_empty_state(*, page: str, custom_title: str | None = None) -> dict:
    state = EMPTY_STATES.get(page, {"icon": "📭", "title": "Nothing here",
                                      "description": "This section is empty.", "cta_label": None, "cta_action": None})
    if custom_title:
        state = {**state, "title": html.escape(custom_title)}
    return {**state, "page": page}
