"""Manifest Parser — parse and validate extension app manifests.

Parses manifest.json files with schema validation, version requirement
checking, entrypoint resolution, and dependency extraction.
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass, field
from enum import Enum


class ManifestVersion(str, Enum):
    V1 = "1.0"
    V2 = "2.0"


REQUIRED_V1 = {"name", "version", "entrypoint", "permissions"}
REQUIRED_V2 = {"name", "version", "entrypoint", "permissions", "sdk_version", "runtime"}
VALID_RUNTIMES = {"node18", "node20", "python3.11", "python3.12", "deno", "bun"}
SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+(-[\w.]+)?(\+[\w.]+)?$")


@dataclass
class ParsedManifest:
    name: str
    version: str
    manifest_version: ManifestVersion
    entrypoint: str
    permissions: list[str]
    runtime: str = ""
    sdk_version: str = ""
    dependencies: dict[str, str] = field(default_factory=dict)
    description: str = ""
    author: str = ""
    icon: str = ""
    min_platform_version: str = ""


@dataclass
class ParseResult:
    valid: bool
    manifest: ParsedManifest | None = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ManifestParserService:
    """Parses and validates extension manifests."""

    def parse(self, raw: str) -> ParseResult:
        errors: list[str] = []
        warnings: list[str] = []

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            return ParseResult(valid=False, errors=[f"Invalid JSON: {e}"])

        if not isinstance(data, dict):
            return ParseResult(valid=False, errors=["Manifest must be a JSON object"])

        # Determine version
        mv = data.get("manifest_version", "1.0")
        try:
            manifest_version = ManifestVersion(mv)
        except ValueError:
            return ParseResult(valid=False, errors=[f"Unknown manifest_version: {mv}"])

        # Check required fields
        required = REQUIRED_V2 if manifest_version == ManifestVersion.V2 else REQUIRED_V1
        for field_name in required:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")

        # Validate version
        version = data.get("version", "")
        if version and not SEMVER_RE.match(version):
            errors.append(f"Invalid semver: {version}")

        # Validate runtime (v2)
        runtime = data.get("runtime", "")
        if manifest_version == ManifestVersion.V2 and runtime and runtime not in VALID_RUNTIMES:
            errors.append(f"Unsupported runtime: {runtime}")

        # Validate entrypoint
        entrypoint = data.get("entrypoint", "")
        if entrypoint and ".." in entrypoint:
            errors.append("Entrypoint must not contain path traversal")

        # Validate permissions
        permissions = data.get("permissions", [])
        if not isinstance(permissions, list):
            errors.append("permissions must be an array")
            permissions = []

        if errors:
            return ParseResult(valid=False, errors=errors, warnings=warnings)

        # Warnings
        if not data.get("description"):
            warnings.append("Missing description")
        if not data.get("author"):
            warnings.append("Missing author")

        deps = data.get("dependencies", {})
        if not isinstance(deps, dict):
            warnings.append("dependencies should be an object")
            deps = {}

        manifest = ParsedManifest(
            name=data["name"], version=data["version"],
            manifest_version=manifest_version,
            entrypoint=data["entrypoint"], permissions=permissions,
            runtime=runtime, sdk_version=data.get("sdk_version", ""),
            dependencies=deps, description=data.get("description", ""),
            author=data.get("author", ""), icon=data.get("icon", ""),
            min_platform_version=data.get("min_platform_version", ""),
        )

        return ParseResult(valid=True, manifest=manifest, warnings=warnings)

    def validate_compatibility(self, manifest: ParsedManifest,
                               platform_version: str) -> dict:
        issues = []
        if manifest.min_platform_version:
            if manifest.min_platform_version > platform_version:
                issues.append(f"Requires platform {manifest.min_platform_version}, current is {platform_version}")
        return {"compatible": len(issues) == 0, "issues": issues}
