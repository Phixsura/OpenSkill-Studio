"""Complete app create flow — guided app creation with templates and validation."""


def build_app_create_flow(*, templates: list[dict], categories: list[dict]) -> dict:
    return {
        "page_type": "create_app",
        "methods": [
            {"key": "template", "title": "Start from Template", "icon": "📋",
             "description": "Choose a starter template", "templates": templates[:6]},
            {"key": "scratch", "title": "Start from Scratch", "icon": "✏️",
             "description": "Build from the ground up"},
            {"key": "import", "title": "Import Existing", "icon": "📥",
             "description": "Import from GitHub or ZIP"},
        ],
        "form": {
            "fields": [
                {"name": "name", "label": "App Name", "type": "text", "required": True, "max_length": 50},
                {"name": "slug", "label": "URL Slug", "type": "slug", "required": True, "auto_from": "name"},
                {"name": "category", "label": "Category", "type": "select", "required": True, "options": categories},
                {"name": "description", "label": "Description", "type": "textarea", "required": True, "max_length": 2000},
                {"name": "short_description", "label": "Short Description", "type": "text", "required": False, "max_length": 120},
            ],
        },
        "categories": categories,
    }


def validate_app_name(*, name: str, existing_names: list[str]) -> dict:
    errors = []
    if len(name) < 3:
        errors.append("Name must be at least 3 characters")
    if len(name) > 50:
        errors.append("Name must be under 50 characters")
    if name.lower() in [n.lower() for n in existing_names]:
        errors.append("An app with this name already exists")
    return {"valid": len(errors) == 0, "errors": errors,
            "suggested_slug": name.lower().replace(" ", "-").replace("_", "-")}
