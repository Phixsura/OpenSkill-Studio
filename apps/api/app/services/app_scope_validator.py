"""OAuth scope validator — validates requested scopes against manifest permissions."""

from app.services.manifest_validator import VALID_PERMISSIONS


def validate_scopes(requested: list[str], manifest_permissions: list[str]) -> dict:
    """Validate OAuth scopes against manifest-declared permissions.
    
    Returns {"valid": bool, "granted": [...], "denied": [...], "errors": [...]}
    """
    errors = []
    granted = []
    denied = []

    for scope in requested:
        if scope not in VALID_PERMISSIONS:
            errors.append(f"Unknown scope: {scope}")
            denied.append(scope)
        elif scope not in manifest_permissions:
            errors.append(f"Scope '{scope}' not declared in manifest")
            denied.append(scope)
        else:
            granted.append(scope)

    return {
        "valid": len(errors) == 0,
        "granted": granted,
        "denied": denied,
        "errors": errors,
    }


def parse_scope_string(scope_string: str) -> list[str]:
    """Parse a space-separated scope string into a list."""
    return [s.strip() for s in scope_string.split() if s.strip()]


def format_scope_string(scopes: list[str]) -> str:
    """Format a list of scopes into a space-separated string."""
    return " ".join(sorted(scopes))
