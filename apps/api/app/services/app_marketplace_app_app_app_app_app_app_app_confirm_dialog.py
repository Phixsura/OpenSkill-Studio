"""Confirmation dialog builder — structured confirmation for destructive actions."""
from __future__ import annotations
import html


PRESETS = {
    "delete_app": {"title": "Delete App?", "body": "This will permanently delete the app and all its data.",
                    "confirm_label": "Delete", "variant": "danger", "requires_name": True},
    "revoke_key": {"title": "Revoke API Key?", "body": "Any integrations using this key will stop working.",
                    "confirm_label": "Revoke", "variant": "warning", "requires_name": False},
    "deploy_prod": {"title": "Deploy to Production?", "body": "This will update the live environment.",
                     "confirm_label": "Deploy", "variant": "primary", "requires_name": False},
    "remove_member": {"title": "Remove Team Member?", "body": "They will lose access to this organization.",
                       "confirm_label": "Remove", "variant": "danger", "requires_name": False},
}


def build_dialog(action: str, *, resource_name: str = "") -> dict:
    preset = PRESETS.get(action)
    if not preset:
        return {"error": f"Unknown action: {action}"}
    safe_name = html.escape(resource_name)
    body = preset["body"]
    if preset["requires_name"] and resource_name:
        body += f' Type "{safe_name}" to confirm.'
    return {**preset, "body": body, "resource_name": safe_name, "action": action}
