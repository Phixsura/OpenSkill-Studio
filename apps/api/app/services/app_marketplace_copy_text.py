"""Copy text — centralized UI copy/microcopy for consistency."""

COPY = {
    "cta_install": "Install App",
    "cta_uninstall": "Uninstall",
    "cta_update": "Update Available",
    "cta_publish": "Publish to Marketplace",
    "cta_create_app": "Create New App",
    "cta_get_started": "Get Started",
    "cta_view_docs": "View Documentation",
    "cta_contact_support": "Contact Support",
    "empty_apps": "No apps found. Try adjusting your search or filters.",
    "empty_reviews": "No reviews yet. Be the first to share your experience!",
    "empty_webhooks": "No webhooks configured. Set up your first webhook to receive real-time events.",
    "empty_notifications": "All caught up! No new notifications.",
    "error_generic": "Something went wrong. Please try again.",
    "error_network": "Network error. Check your connection and try again.",
    "error_permission": "You don't have permission to perform this action.",
    "success_install": "App installed successfully!",
    "success_save": "Changes saved.",
    "success_deploy": "Deployed successfully!",
    "confirm_delete": "Are you sure? This action cannot be undone.",
    "confirm_uninstall": "This will remove the app and all its data.",
}


def get_copy(*, key: str, fallback: str = "") -> str:
    return COPY.get(key, fallback)


def get_copy_with_params(*, key: str, params: dict) -> str:
    template = COPY.get(key, "")
    try:
        return template.format(**params)
    except (KeyError, IndexError):
        return template


def get_all_copy(*, prefix: str | None = None) -> dict[str, str]:
    if prefix:
        return {k: v for k, v in COPY.items() if k.startswith(prefix)}
    return dict(COPY)
