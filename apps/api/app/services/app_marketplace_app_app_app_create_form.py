"""App create form — new app creation wizard."""

import html
import re
import secrets

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")
CATEGORIES = ["tools", "productivity", "communication", "analytics", "security",
              "integration", "automation", "monitoring", "testing", "other"]


def validate_app_creation(*, name: str, slug: str, description: str,
                             category: str) -> dict:
    errors = []
    if not name.strip() or len(name) > 64:
        errors.append("Name required (max 64 chars)")
    if not SLUG_RE.match(slug):
        errors.append("Slug: lowercase, digits, hyphens, 3-64 chars")
    if len(description) < 10:
        errors.append("Description must be at least 10 characters")
    if category not in CATEGORIES:
        errors.append(f"Category must be one of: {', '.join(CATEGORIES)}")
    if errors:
        return {"valid": False, "errors": errors}
    return {
        "valid": True,
        "app": {
            "id": f"app_{secrets.token_hex(8)}",
            "name": html.escape(name), "slug": slug,
            "description": html.escape(description),
            "category": category, "version": "0.1.0",
            "status": "draft",
        },
    }
