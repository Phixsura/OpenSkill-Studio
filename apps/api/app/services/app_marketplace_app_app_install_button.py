"""Install button — smart install button with state management."""


def build_install_button(*, installed: bool, installing: bool = False,
                           price: float = 0, plan_required: str | None = None,
                           permissions_count: int = 0) -> dict:
    if installing:
        return {"label": "Installing...", "icon": "⏳", "variant": "loading",
                "disabled": True, "action": None}
    if installed:
        return {"label": "Installed ✓", "icon": "✅", "variant": "installed",
                "disabled": False, "action": "open",
                "secondary_label": "Uninstall", "secondary_action": "uninstall"}
    label = "Install Free" if price == 0 else f"Install — ${price:.2f}/mo"
    return {
        "label": label,
        "icon": "📥",
        "variant": "install",
        "disabled": False,
        "action": "install",
        "plan_required": plan_required,
        "permissions_count": permissions_count,
        "show_permissions": permissions_count > 0,
    }
