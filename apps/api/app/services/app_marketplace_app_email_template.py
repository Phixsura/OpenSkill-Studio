"""Email template — manage transactional email templates for apps."""

import html
import re


TEMPLATE_VARS_RE = re.compile(r"\{\{(\w+)\}\}")


def render_template(*, template: str, variables: dict) -> dict:
    missing = []
    placeholders = TEMPLATE_VARS_RE.findall(template)
    for var in placeholders:
        if var not in variables:
            missing.append(var)
    if missing:
        return {"error": f"Missing variables: {', '.join(missing)}"}
    rendered = template
    for var, value in variables.items():
        safe_value = html.escape(str(value))
        rendered = rendered.replace(f"{{{{{var}}}}}", safe_value)
    return {"rendered": rendered, "variables_used": sorted(set(placeholders)),
            "char_count": len(rendered)}


def list_templates() -> dict:
    return {
        "templates": [
            {"id": "welcome", "name": "Welcome Email", "subject": "Welcome to {{app_name}}!",
             "variables": ["app_name", "user_name"]},
            {"id": "install", "name": "App Installed", "subject": "{{app_name}} installed",
             "variables": ["app_name", "user_name", "install_date"]},
            {"id": "update", "name": "App Updated", "subject": "{{app_name}} v{{version}}",
             "variables": ["app_name", "version", "changelog"]},
        ],
        "total": 3,
    }
