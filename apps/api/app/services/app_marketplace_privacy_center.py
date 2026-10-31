"""Privacy center — GDPR/CCPA privacy controls for marketplace users."""


def build_privacy_center(*, user: dict, data_categories: list[dict],
                             consent: dict, export_available: bool) -> dict:
    return {
        "page_type": "privacy_center",
        "user": {"name": user.get("display_name"), "email": user.get("email")},
        "sections": [
            {"key": "consent", "title": "Cookie & Data Consent", "icon": "🍪",
             "data": consent},
            {"key": "data", "title": "Your Data", "icon": "📋",
             "categories": data_categories,
             "export_available": export_available},
            {"key": "rights", "title": "Your Rights", "icon": "⚖️",
             "rights": ["Access your data", "Export your data", "Delete your data",
                          "Restrict processing", "Object to processing", "Data portability"]},
            {"key": "delete", "title": "Delete Account", "icon": "🗑️",
             "warning": "This action is permanent and cannot be undone."},
        ],
    }


def request_data_deletion(*, user_id: str, reason: str) -> dict:
    return {"user_id": user_id, "reason": reason, "status": "pending",
            "message": "Your deletion request has been received. Processing takes up to 30 days.",
            "confirmation_required": True}
