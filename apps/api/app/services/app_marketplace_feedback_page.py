"""Feedback page — collect user feedback about the platform."""


def build_feedback_page(*, user: dict | None) -> dict:
    categories = [
        {"id": "bug", "label": "Bug Report", "icon": "🐛", "description": "Something isn't working"},
        {"id": "feature", "label": "Feature Request", "icon": "💡", "description": "Suggest a new feature"},
        {"id": "improvement", "label": "Improvement", "icon": "✨", "description": "Make something better"},
        {"id": "docs", "label": "Documentation", "icon": "📚", "description": "Docs feedback"},
        {"id": "other", "label": "Other", "icon": "💬", "description": "General feedback"},
    ]
    return {
        "page_type": "feedback",
        "categories": categories,
        "authenticated": user is not None,
        "form_fields": [
            {"name": "category", "type": "select", "required": True},
            {"name": "title", "type": "text", "required": True, "max_length": 100},
            {"name": "description", "type": "textarea", "required": True, "max_length": 2000},
            {"name": "email", "type": "email", "required": user is None},
            {"name": "screenshot", "type": "file", "required": False},
        ],
    }


def submit_feedback(*, category: str, title: str, description: str,
                       email: str | None = None) -> dict:
    if len(title) < 5:
        return {"success": False, "error": "Title must be at least 5 characters"}
    if len(description) < 20:
        return {"success": False, "error": "Description must be at least 20 characters"}
    return {"success": True, "message": "Thank you for your feedback!",
            "ticket_id": f"FB-{abs(hash(title)) % 10000:04d}"}
