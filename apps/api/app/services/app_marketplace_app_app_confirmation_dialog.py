"""Confirmation dialog — destructive action confirmation builder."""

import html

PRESETS = {
    "delete_app": {"title": "Delete App", "icon": "🗑️", "severity": "danger",
                    "message": "This will permanently delete the app and all associated data.",
                    "confirm_text": "DELETE"},
    "revoke_token": {"title": "Revoke Token", "icon": "🔑", "severity": "warning",
                      "message": "This will immediately revoke the token. All API calls using it will fail.",
                      "confirm_text": "REVOKE"},
    "remove_member": {"title": "Remove Member", "icon": "👤", "severity": "warning",
                       "message": "This person will lose access to the organization.",
                       "confirm_text": "REMOVE"},
    "reset_data": {"title": "Reset Data", "icon": "💥", "severity": "danger",
                    "message": "All data will be permanently erased. This cannot be undone.",
                    "confirm_text": "RESET"},
}


def build_confirmation(*, preset: str | None = None, title: str = "",
                         message: str = "", confirm_text: str = "CONFIRM") -> dict:
    if preset and preset in PRESETS:
        p = PRESETS[preset]
        return {**p, "requires_text_input": True, "preset": preset}
    return {"title": html.escape(title), "message": html.escape(message),
            "confirm_text": confirm_text, "icon": "⚠️", "severity": "warning",
            "requires_text_input": len(confirm_text) > 3, "preset": None}
