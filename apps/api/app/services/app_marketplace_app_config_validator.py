"""Config validator — validate app manifest and configuration files."""

import re


REQUIRED_FIELDS = ["name", "version", "description", "author", "entry_point"]
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$")


def validate_manifest(*, manifest: dict) -> dict:
    errors = []
    warnings = []
    for field in REQUIRED_FIELDS:
        if not manifest.get(field):
            errors.append({"field": field, "message": f"Missing required field: {field}"})
    version = manifest.get("version", "")
    if version and not VERSION_RE.match(version):
        errors.append({"field": "version", "message": f"Invalid semver: {version}"})
    if not manifest.get("icon"):
        warnings.append({"field": "icon", "message": "No icon specified"})
    if not manifest.get("category"):
        warnings.append({"field": "category", "message": "No category specified"})
    perms = manifest.get("permissions", [])
    if not isinstance(perms, list):
        errors.append({"field": "permissions", "message": "Permissions must be a list"})
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "error_count": len(errors),
        "warning_count": len(warnings),
        "fields_present": sum(1 for f in REQUIRED_FIELDS if manifest.get(f)),
        "fields_required": len(REQUIRED_FIELDS),
    }
