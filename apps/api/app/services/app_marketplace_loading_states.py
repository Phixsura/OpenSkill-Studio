"""Loading states — standardized loading/skeleton state data for UI components."""


def build_loading_state(*, component: str, item_count: int = 3) -> dict:
    skeletons = {
        "app_card": {"width": "100%", "height": "180px", "elements": ["icon", "title", "description", "rating"]},
        "app_list": {"width": "100%", "height": "60px", "elements": ["icon", "name", "category"]},
        "review": {"width": "100%", "height": "120px", "elements": ["avatar", "name", "stars", "text"]},
        "stat_card": {"width": "200px", "height": "100px", "elements": ["value", "label"]},
        "table_row": {"width": "100%", "height": "40px", "elements": ["col1", "col2", "col3"]},
    }
    skeleton = skeletons.get(component, {"width": "100%", "height": "100px", "elements": ["content"]})
    return {"component": component, "skeleton": skeleton, "count": item_count,
            "animation": "pulse", "items": [skeleton] * item_count}


def get_error_state(*, component: str, error: str, retryable: bool = True) -> dict:
    return {"component": component, "error": error, "retryable": retryable,
            "icon": "❌", "action": "Retry" if retryable else "Go Back"}


def get_empty_state_for_component(*, component: str) -> dict:
    messages = {
        "app_list": {"icon": "📦", "title": "No apps found", "message": "Try adjusting your search"},
        "reviews": {"icon": "⭐", "title": "No reviews yet", "message": "Be the first to leave a review"},
        "webhooks": {"icon": "🔗", "title": "No webhooks", "message": "Set up your first webhook"},
        "notifications": {"icon": "🔔", "title": "All caught up!", "message": "No new notifications"},
    }
    return messages.get(component, {"icon": "📭", "title": "Nothing here", "message": ""})
