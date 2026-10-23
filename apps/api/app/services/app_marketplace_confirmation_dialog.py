"""Confirmation dialog — standardized confirmation prompts for destructive actions."""

CONFIRMATIONS = {
    "uninstall": {"title": "Uninstall App", "message": "This will remove the app and all its data. This cannot be undone.",
                   "confirm_label": "Uninstall", "danger": True, "requires_typing": False},
    "delete_app": {"title": "Delete App", "message": "This will permanently delete your app and all versions.",
                    "confirm_label": "Delete Forever", "danger": True, "requires_typing": True, "typing_text": "DELETE"},
    "revoke_key": {"title": "Revoke API Key", "message": "This key will stop working immediately. Active sessions may be affected.",
                    "confirm_label": "Revoke", "danger": True, "requires_typing": False},
    "transfer": {"title": "Transfer Ownership", "message": "You will lose ownership of this app. This cannot be reversed.",
                  "confirm_label": "Transfer", "danger": True, "requires_typing": True, "typing_text": "TRANSFER"},
    "deploy": {"title": "Deploy to Production", "message": "This version will be live for all users.",
                "confirm_label": "Deploy", "danger": False, "requires_typing": False},
}


def get_confirmation(*, action: str, context: dict | None = None) -> dict:
    conf = CONFIRMATIONS.get(action)
    if not conf:
        return {"title": "Confirm", "message": "Are you sure?", "confirm_label": "Confirm",
                "danger": False, "requires_typing": False}
    result = dict(conf)
    if context:
        result["message"] = result["message"].replace("{app_name}", context.get("app_name", "this app"))
    return result
