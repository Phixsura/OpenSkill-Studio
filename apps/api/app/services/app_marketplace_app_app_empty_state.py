"""Empty state — generate contextual empty state content."""


EMPTY_STATES = {
    "no_apps": {"title": "No Apps Yet", "icon": "📦", "description": "Create your first app to get started.",
                "cta_label": "Create App", "cta_url": "/apps/new"},
    "no_reviews": {"title": "No Reviews", "icon": "⭐", "description": "Your app hasn't received any reviews yet.",
                   "cta_label": "Share Your App", "cta_url": "/apps/share"},
    "no_installs": {"title": "No Installs", "icon": "📥", "description": "Promote your app to get your first install.",
                    "cta_label": "Optimization Tips", "cta_url": "/docs/marketing"},
    "no_webhooks": {"title": "No Webhooks", "icon": "🪝", "description": "Set up webhooks to receive real-time events.",
                    "cta_label": "Add Webhook", "cta_url": "/webhooks/new"},
    "no_analytics": {"title": "No Data Yet", "icon": "📊", "description": "Analytics will appear once users start using your app.",
                     "cta_label": "Learn More", "cta_url": "/docs/analytics"},
    "no_results": {"title": "No Results", "icon": "🔍", "description": "Try adjusting your search or filters.",
                   "cta_label": "Clear Filters", "cta_url": None},
    "error": {"title": "Something Went Wrong", "icon": "💥", "description": "We encountered an error. Please try again.",
              "cta_label": "Retry", "cta_url": None},
}


def get_empty_state(*, state_type: str) -> dict:
    state = EMPTY_STATES.get(state_type, EMPTY_STATES["error"])
    return {"type": state_type, **state}
