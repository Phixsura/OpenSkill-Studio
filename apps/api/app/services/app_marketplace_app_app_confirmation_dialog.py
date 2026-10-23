"""Confirmation dialog — generate typed confirmation prompts for dangerous actions."""


DIALOG_TEMPLATES = {
    "delete_app": {"title": "Delete App?", "icon": "🗑️", "danger": True,
                    "message": "This will permanently delete the app and all its data. This action cannot be undone.",
                    "confirm_text": "DELETE", "cancel_label": "Keep App"},
    "revoke_key": {"title": "Revoke API Key?", "icon": "🔑", "danger": True,
                    "message": "This will immediately invalidate the key. Any services using it will stop working.",
                    "confirm_text": "REVOKE", "cancel_label": "Cancel"},
    "deploy_production": {"title": "Deploy to Production?", "icon": "🚀", "danger": False,
                           "message": "This will deploy the current build to production.",
                           "confirm_text": None, "cancel_label": "Cancel"},
    "cancel_subscription": {"title": "Cancel Subscription?", "icon": "💳", "danger": True,
                              "message": "Your subscription will end at the current billing period.",
                              "confirm_text": "CANCEL", "cancel_label": "Keep Subscription"},
}


def get_confirmation(*, action: str, context: dict | None = None) -> dict:
    template = DIALOG_TEMPLATES.get(action)
    if not template:
        return {"error": f"Unknown action. Valid: {', '.join(sorted(DIALOG_TEMPLATES))}"}
    result = {**template, "action": action}
    if context:
        result["message"] = result["message"].replace("{name}", context.get("name", ""))
    return result
