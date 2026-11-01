"""App settings general — general app settings page builder."""

import html
import re

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
CATEGORIES = ["tools", "productivity", "communication", "analytics", "security",
              "integration", "automation", "monitoring", "testing", "other"]


def build_general_settings(*, app: dict) -> dict:
    return {
        "fields": [
            {"key": "name", "label": "App Name", "type": "text", "value": html.escape(app.get("name", "")),
             "required": True, "max_length": 64},
            {"key": "slug", "label": "URL Slug", "type": "text", "value": app.get("slug", ""),
             "required": True, "help": "Lowercase, digits, hyphens. 3-64 chars."},
            {"key": "tagline", "label": "Tagline", "type": "text", "value": html.escape(app.get("tagline", "")),
             "max_length": 120},
            {"key": "description", "label": "Description", "type": "textarea",
             "value": html.escape(app.get("description", "")), "max_length": 2000},
            {"key": "icon", "label": "Icon", "type": "emoji", "value": app.get("icon", "📦")},
            {"key": "category", "label": "Category", "type": "select",
             "value": app.get("category", "other"), "options": CATEGORIES},
            {"key": "website", "label": "Website URL", "type": "url",
             "value": app.get("website", "")},
            {"key": "support_email", "label": "Support Email", "type": "email",
             "value": app.get("support_email", "")},
        ],
        "app_id": app.get("id", ""),
        "current_version": app.get("version", "1.0.0"),
    }


def validate_general_settings(*, data: dict) -> dict:
    errors = []
    if not data.get("name", "").strip():
        errors.append("App name is required")
    slug = data.get("slug", "")
    if not SLUG_RE.match(slug):
        errors.append("Invalid slug format")
    if len(data.get("description", "")) < 10:
        errors.append("Description must be at least 10 characters")
    return {"valid": len(errors) == 0, "errors": errors}
