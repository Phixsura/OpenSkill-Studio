"""Extension Manifest — parse, validate, and manage extension manifest files.

The manifest.json is the central configuration file for every extension,
declaring metadata, permissions, entry points, and dependencies.
"""
from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_FIELDS = {"name", "version", "type", "entry_point"}
VALID_TYPES = {"connector", "widget", "automation", "theme", "tool", "analytics"}
MANIFEST_VERSION = "1.0"


@dataclass
class ManifestValidationResult:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class ExtensionManifest:
    name: str
    version: str
    type: str
    entry_point: str
    description: str = ""
    author: str = ""
    license: str = "MIT"
    homepage: str = ""
    repository: str = ""
    permissions: list[str] = field(default_factory=list)
    dependencies: dict[str, str] = field(default_factory=dict)
    config_schema: dict = field(default_factory=dict)
    min_platform_version: str = "1.0.0"
    icons: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


def parse_manifest(data: dict) -> tuple[ExtensionManifest | None, ManifestValidationResult]:
    """Parse and validate a manifest dict into an ExtensionManifest."""
    errors = []
    warnings = []

    # Check required fields
    for f in REQUIRED_FIELDS:
        if f not in data or not data[f]:
            errors.append(f"Missing required field: {f}")

    if errors:
        return None, ManifestValidationResult(False, errors)

    # Validate type
    if data["type"] not in VALID_TYPES:
        errors.append(f"Invalid type '{data['type']}'. Must be one of: {', '.join(sorted(VALID_TYPES))}")

    # Validate version format
    version = data.get("version", "")
    parts = version.split(".")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        errors.append(f"Invalid version '{version}'. Must be semver (e.g., 1.0.0)")

    # Validate permissions
    for perm in data.get("permissions", []):
        if "." not in perm:
            warnings.append(f"Permission '{perm}' should use dotted notation (e.g., projects.read)")

    # Validate dependencies
    for dep_name, dep_ver in data.get("dependencies", {}).items():
        if not dep_ver:
            warnings.append(f"Dependency '{dep_name}' has no version constraint")

    # Warnings for optional but recommended fields
    if not data.get("description"):
        warnings.append("Missing recommended field: description")
    if not data.get("author"):
        warnings.append("Missing recommended field: author")
    if not data.get("tags"):
        warnings.append("No tags specified — extension may be hard to discover")

    if errors:
        return None, ManifestValidationResult(False, errors, warnings)

    manifest = ExtensionManifest(
        name=data["name"], version=data["version"],
        type=data["type"], entry_point=data["entry_point"],
        description=data.get("description", ""),
        author=data.get("author", ""),
        license=data.get("license", "MIT"),
        homepage=data.get("homepage", ""),
        repository=data.get("repository", ""),
        permissions=data.get("permissions", []),
        dependencies=data.get("dependencies", {}),
        config_schema=data.get("config_schema", {}),
        min_platform_version=data.get("min_platform_version", "1.0.0"),
        icons=data.get("icons", {}),
        tags=data.get("tags", []),
    )
    return manifest, ManifestValidationResult(True, [], warnings)


def merge_manifests(base: dict, override: dict) -> dict:
    """Merge two manifest dicts (e.g., default + environment-specific)."""
    merged = {**base}
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = {**merged[key], **value}
        elif isinstance(value, list) and isinstance(merged.get(key), list):
            merged[key] = list(set(merged[key] + value))
        else:
            merged[key] = value
    return merged
