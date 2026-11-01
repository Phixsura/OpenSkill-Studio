"""Toast notifications — transient notification system for user feedback."""


def create_toast(*, type: str, title: str, message: str = "",
                    duration_ms: int = 5000, dismissible: bool = True) -> dict:
    valid_types = {"success", "error", "warning", "info"}
    if type not in valid_types:
        type = "info"
    icons = {"success": "✅", "error": "❌", "warning": "⚠️", "info": "ℹ️"}
    return {"type": type, "title": title, "message": message, "icon": icons[type],
            "duration_ms": duration_ms, "dismissible": dismissible, "visible": True}


def create_action_toast(*, action: str, entity: str, success: bool) -> dict:
    actions = {
        "install": {"success": f"{entity} installed successfully!", "error": f"Failed to install {entity}"},
        "uninstall": {"success": f"{entity} uninstalled", "error": f"Failed to uninstall {entity}"},
        "update": {"success": f"{entity} updated!", "error": f"Failed to update {entity}"},
        "save": {"success": "Changes saved", "error": "Failed to save changes"},
        "delete": {"success": f"{entity} deleted", "error": f"Failed to delete {entity}"},
        "deploy": {"success": f"{entity} deployed!", "error": f"Deployment failed for {entity}"},
    }
    msgs = actions.get(action, {"success": "Action completed", "error": "Action failed"})
    return create_toast(type="success" if success else "error", title=msgs["success" if success else "error"])


def build_toast_queue(*, toasts: list[dict], max_visible: int = 3) -> dict:
    visible = [t for t in toasts if t.get("visible")][:max_visible]
    return {"visible": visible, "queued": max(0, len(toasts) - max_visible), "total": len(toasts)}
