"""Manifest template generator — scaffold manifests for common app types."""


TEMPLATES = {
    "connector": {
        "schema_version": "1.0",
        "app": {"name": "", "slug": "", "version": "1.0.0", "category": "connector"},
        "permissions": ["read:cohorts", "read:submissions", "write:project_results", "subscribe:events"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60,
                     "network": {"allowed_hosts": [], "egress_policy": "allowlist"}},
        "event_subscriptions": ["submission.completed"],
        "secrets": [{"key": "API_KEY", "required": True}],
        "config_schema": {"type": "object", "properties": {"base_url": {"type": "string"}}, "required": ["base_url"]},
    },
    "automation": {
        "schema_version": "1.0",
        "app": {"name": "", "slug": "", "version": "1.0.0", "category": "automation"},
        "permissions": ["read:submissions", "write:evaluations", "subscribe:events", "run:background_jobs"],
        "sandbox": {"runtime": "nodejs20", "memory_mb": 128, "timeout_seconds": 30},
        "event_subscriptions": ["submission.completed"],
    },
    "analytics": {
        "schema_version": "1.0",
        "app": {"name": "", "slug": "", "version": "1.0.0", "category": "analytics"},
        "permissions": ["read:cohorts", "read:skills", "read:analytics", "export:analytics"],
    },
    "ui_extension": {
        "schema_version": "1.0",
        "app": {"name": "", "slug": "", "version": "1.0.0", "category": "ui_extension"},
        "permissions": ["read:cohorts", "read:projects", "extend:ui"],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "", "entry": "index.html",
             "viewport": {"width": 400, "height": 300}},
        ],
    },
    "ecosystem_source": {
        "schema_version": "1.0",
        "app": {"name": "", "slug": "", "version": "1.0.0", "category": "ecosystem_source"},
        "permissions": ["read:talent", "write:talent"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 128, "timeout_seconds": 120,
                     "network": {"allowed_hosts": [], "egress_policy": "allowlist"}},
        "secrets": [{"key": "API_KEY", "required": True}],
    },
}


def get_template(category: str) -> dict | None:
    """Get a manifest template for a category."""
    import copy
    template = TEMPLATES.get(category)
    return copy.deepcopy(template) if template else None


def fill_template(category: str, *, name: str, slug: str) -> dict | None:
    """Get a pre-filled manifest template."""
    template = get_template(category)
    if not template:
        return None
    template["app"]["name"] = name
    template["app"]["slug"] = slug
    if template.get("ui_extensions"):
        for ext in template["ui_extensions"]:
            if not ext.get("title"):
                ext["title"] = name
    return template


def list_templates() -> list[dict]:
    """List available manifest templates."""
    return [{"category": cat, "description": f"{cat.replace('_', ' ').title()} template"} for cat in TEMPLATES]
