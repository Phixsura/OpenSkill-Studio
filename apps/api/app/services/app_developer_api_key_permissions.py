"""API key permissions — validate and enforce per-key scope restrictions."""


def validate_key_scopes(requested_scopes: list[str], app_permissions: list[str]) -> dict:
    """Validate that requested key scopes are subset of app permissions."""
    requested = set(requested_scopes)
    allowed = set(app_permissions)
    denied = requested - allowed
    granted = requested & allowed
    return {"valid": len(denied) == 0, "granted": sorted(granted), "denied": sorted(denied)}


def check_key_access(key_scopes: list[str], required_scope: str) -> bool:
    """Check if an API key has the required scope."""
    return required_scope in key_scopes
