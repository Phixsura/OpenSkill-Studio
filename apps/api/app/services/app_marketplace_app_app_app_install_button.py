"""App install button — smart install button state management."""

import html


def build_install_button(*, app: dict, user_installed: bool = False,
                           user_plan: str = "free") -> dict:
    pricing = app.get("pricing", "Free")
    is_free = pricing == "Free" or pricing == "$0"
    min_plan = app.get("min_plan", "free")
    plan_order = {"free": 0, "starter": 1, "pro": 2, "enterprise": 3}
    has_required_plan = plan_order.get(user_plan, 0) >= plan_order.get(min_plan, 0)
    if user_installed:
        return {"state": "installed", "label": "Installed ✓", "disabled": True,
                "action": "open", "variant": "secondary"}
    if not has_required_plan:
        return {"state": "upgrade_required", "label": f"Requires {min_plan.title()} plan",
                "disabled": False, "action": "upgrade", "variant": "warning"}
    if is_free:
        return {"state": "install", "label": "Install — Free", "disabled": False,
                "action": "install", "variant": "primary"}
    return {"state": "subscribe", "label": f"Subscribe — {pricing}",
            "disabled": False, "action": "subscribe", "variant": "primary"}
