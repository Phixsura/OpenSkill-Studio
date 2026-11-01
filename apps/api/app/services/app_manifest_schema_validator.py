"""Manifest JSON Schema validator — validate manifest against formal schema."""

MANIFEST_SCHEMA = {
    "required_fields": {
        "schema_version": str,
        "app": dict,
    },
    "app_required": {
        "name": str,
        "slug": str,
        "version": str,
        "category": str,
    },
    "optional_sections": ["permissions", "sandbox", "event_subscriptions", "ui_extensions", "secrets", "config_schema"],
}


def validate_schema_structure(manifest: dict) -> list[str]:
    """Validate manifest has correct structure."""
    errors = []
    if not isinstance(manifest, dict):
        return ["Manifest must be a JSON object"]
    
    for field, expected_type in MANIFEST_SCHEMA["required_fields"].items():
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
        elif not isinstance(manifest[field], expected_type):
            errors.append(f"Field '{field}' must be {expected_type.__name__}")
    
    app = manifest.get("app", {})
    if isinstance(app, dict):
        for field, expected_type in MANIFEST_SCHEMA["app_required"].items():
            if field not in app:
                errors.append(f"Missing app.{field}")
            elif not isinstance(app[field], expected_type):
                errors.append(f"app.{field} must be {expected_type.__name__}")
    
    return errors
