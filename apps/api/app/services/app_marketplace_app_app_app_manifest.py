"""App manifest — app.json manifest validator and builder."""

import html
import re

REQUIRED_FIELDS = {"name", "version", "description", "author"}
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$")


def validate_manifest(*, manifest: dict) -> dict:
    errors = []
    warnings = []
    for field in REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
    name = manifest.get("name", "")
    if name and not SLUG_RE.match(name):
        errors.append("Name must be lowercase alphanumeric with hyphens (3-64 chars)")
    version = manifest.get("version", "")
    if version and not re.match(r"^\d+\.\d+\.\d+$", version):
        errors.append("Version must be semver (x.y.z)")
    if not manifest.get("icon"):
        warnings.append("No icon specified")
    if not manifest.get("permissions"):
        warnings.append("No permissions declared")
    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings,
            "field_count": len(manifest)}


def build_manifest(*, name: str, version: str, description: str,
                     author: str, permissions: list[str] | None = None) -> dict:
    return {"name": name, "version": version,
            "description": html.escape(description),
            "author": html.escape(author),
            "permissions": permissions or [],
            "engines": {"node": ">=18"}, "main": "index.js"}
