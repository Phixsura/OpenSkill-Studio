"""Modal manager — centralized modal state management."""


def create_modal(*, modal_id: str, title: str, size: str = "md",
                    closeable: bool = True, overlay: bool = True) -> dict:
    valid_sizes = {"sm", "md", "lg", "xl", "full"}
    size = size if size in valid_sizes else "md"
    size_classes = {"sm": "max-w-sm", "md": "max-w-md", "lg": "max-w-lg", "xl": "max-w-xl", "full": "max-w-full"}
    return {"modal_id": modal_id, "title": title, "size": size,
            "size_class": size_classes[size], "closeable": closeable,
            "overlay": overlay, "open": False}


def get_modal_stack(*, modals: list[dict]) -> dict:
    open_modals = [m for m in modals if m.get("open")]
    return {"stack": open_modals, "depth": len(open_modals),
            "top_modal": open_modals[-1] if open_modals else None,
            "has_overlay": any(m.get("overlay") for m in open_modals)}


STANDARD_MODALS = {
    "install": {"title": "Install App", "size": "md"},
    "uninstall": {"title": "Uninstall App", "size": "sm"},
    "update": {"title": "Update App", "size": "md"},
    "settings": {"title": "App Settings", "size": "lg"},
    "api_key": {"title": "Create API Key", "size": "md"},
    "webhook": {"title": "Add Webhook", "size": "lg"},
    "confirm_delete": {"title": "Confirm Delete", "size": "sm"},
    "share": {"title": "Share App", "size": "sm"},
}


def get_standard_modal(*, modal_type: str) -> dict | None:
    config = STANDARD_MODALS.get(modal_type)
    if not config:
        return None
    return create_modal(modal_id=modal_type, **config)
