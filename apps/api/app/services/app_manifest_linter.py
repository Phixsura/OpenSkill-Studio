"""Manifest linter — suggest improvements beyond basic validation."""


def lint_manifest(manifest: dict) -> list[dict]:
    """Return suggestions for manifest improvements."""
    suggestions = []
    app = manifest.get("app", {})
    
    if not app.get("description") and not manifest.get("description"):
        suggestions.append({"level": "warning", "field": "app.description", "message": "Add a description to help users understand your app"})
    
    perms = manifest.get("permissions", [])
    if len(perms) > 15:
        suggestions.append({"level": "info", "field": "permissions", "message": f"Consider reducing permissions ({len(perms)} requested) — fewer permissions increase trust"})
    
    sandbox = manifest.get("sandbox", {})
    if sandbox.get("memory_mb", 0) > 256:
        suggestions.append({"level": "info", "field": "sandbox.memory_mb", "message": "Consider lowering memory if possible to improve resource efficiency"})
    
    if not manifest.get("config_schema"):
        suggestions.append({"level": "info", "field": "config_schema", "message": "Adding a config_schema helps validate installation configuration"})
    
    secrets = manifest.get("secrets", [])
    for s in secrets:
        if not s.get("description"):
            suggestions.append({"level": "warning", "field": f"secrets.{s.get('key','?')}", "message": f"Add description for secret '{s.get('key','?')}' to guide users"})
    
    return suggestions
