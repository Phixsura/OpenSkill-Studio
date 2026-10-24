"""Success page — post-action success confirmation pages."""


def build_success_page(*, action: str, resource_name: str,
                         next_steps: list[dict] | None = None) -> dict:
    actions = {
        "installed": {"title": f"{resource_name} Installed!", "icon": "🎉", "message": "The app is ready to use."},
        "published": {"title": f"{resource_name} Published!", "icon": "🚀", "message": "Your app is now live on the marketplace."},
        "deployed": {"title": f"Deployed {resource_name}!", "icon": "✅", "message": "Your deployment is live."},
        "deleted": {"title": f"{resource_name} Deleted", "icon": "🗑️", "message": "The resource has been removed."},
        "subscribed": {"title": f"Subscribed to {resource_name}!", "icon": "💳", "message": "Your subscription is active."},
    }
    config = actions.get(action, {"title": "Success!", "icon": "✅", "message": "Action completed."})
    default_steps = [
        {"label": "Go to Dashboard", "url": "/dashboard", "primary": True},
        {"label": "View Details", "url": f"/{action}", "primary": False},
    ]
    return {**config, "action": action, "resource_name": resource_name,
            "next_steps": next_steps or default_steps}
