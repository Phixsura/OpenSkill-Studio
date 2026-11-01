"""App settings v2 — grouped settings with validation and defaults."""


SETTING_GROUPS = {
    "general": {"label": "General", "icon": "⚙️"},
    "security": {"label": "Security", "icon": "🔒"},
    "notifications": {"label": "Notifications", "icon": "🔔"},
    "integrations": {"label": "Integrations", "icon": "🔗"},
    "advanced": {"label": "Advanced", "icon": "🛠️"},
}


def get_settings_schema(*, group: str | None = None) -> dict:
    all_settings = {
        "general": [
            {"key": "app_name", "type": "string", "label": "App Name", "required": True, "max_length": 50},
            {"key": "description", "type": "text", "label": "Description", "required": False, "max_length": 2000},
            {"key": "category", "type": "select", "label": "Category", "options": ["connector", "automation", "analytics"]},
        ],
        "security": [
            {"key": "require_https", "type": "boolean", "label": "Require HTTPS", "default": True},
            {"key": "ip_allowlist", "type": "list", "label": "IP Allowlist", "default": []},
            {"key": "session_timeout_min", "type": "integer", "label": "Session Timeout (min)", "default": 30, "min": 5, "max": 1440},
        ],
        "notifications": [
            {"key": "email_on_install", "type": "boolean", "label": "Email on install", "default": True},
            {"key": "email_on_error", "type": "boolean", "label": "Email on error", "default": True},
            {"key": "slack_webhook", "type": "string", "label": "Slack Webhook URL", "required": False},
        ],
    }
    if group:
        return {"group": group, "settings": all_settings.get(group, [])}
    return {"groups": list(all_settings.keys()), "settings": all_settings}


def validate_setting(*, key: str, value: object, schema: dict) -> dict:
    errors = []
    if schema.get("required") and not value:
        errors.append("This field is required")
    if schema.get("type") == "string" and isinstance(value, str):
        if schema.get("max_length") and len(value) > schema["max_length"]:
            errors.append(f"Maximum length is {schema['max_length']}")
    if schema.get("type") == "integer" and isinstance(value, int):
        if schema.get("min") is not None and value < schema["min"]:
            errors.append(f"Minimum value is {schema['min']}")
        if schema.get("max") is not None and value > schema["max"]:
            errors.append(f"Maximum value is {schema['max']}")
    return {"valid": len(errors) == 0, "errors": errors}
