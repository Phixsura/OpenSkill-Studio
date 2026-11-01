"""Extension Config Validator — validate extension.json manifest files."""
from __future__ import annotations
import re


REQUIRED_FIELDS = {"name", "version", "description", "author", "entry_point"}
OPTIONAL_FIELDS = {"homepage", "repository", "license", "keywords", "permissions",
                   "min_platform_version", "icon", "screenshots", "pricing"}
VERSION_RE = re.compile(r'^\d+\.\d+\.\d+$')
NAME_RE = re.compile(r'^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$')


class ExtConfigValidatorService:
    def validate(self, config: dict) -> tuple[bool, list[str]]:
        errors = []
        warnings = []

        # Required fields
        for field in REQUIRED_FIELDS:
            if field not in config:
                errors.append(f"Missing required field: {field}")

        # Name format
        name = config.get("name", "")
        if name and not NAME_RE.match(name):
            errors.append("Invalid name: must be lowercase alphanumeric with hyphens, 3-64 chars")

        # Version format
        version = config.get("version", "")
        if version and not VERSION_RE.match(version):
            errors.append(f"Invalid version: {version} (must be semver X.Y.Z)")

        # Description length
        desc = config.get("description", "")
        if desc and len(desc) < 10:
            warnings.append("Description should be at least 10 characters")
        if desc and len(desc) > 500:
            errors.append("Description too long (max 500 chars)")

        # Permissions
        perms = config.get("permissions", [])
        if not isinstance(perms, list):
            errors.append("permissions must be an array")

        # Keywords
        keywords = config.get("keywords", [])
        if keywords and len(keywords) > 20:
            errors.append("Too many keywords (max 20)")

        # Unknown fields
        known = REQUIRED_FIELDS | OPTIONAL_FIELDS
        for k in config:
            if k not in known:
                warnings.append(f"Unknown field: {k}")

        return len(errors) == 0, errors + [f"[warn] {w}" for w in warnings]

    def generate_template(self, name: str, author: str) -> dict:
        return {
            "name": name, "version": "0.1.0", "description": "",
            "author": author, "entry_point": "src/index.js",
            "permissions": [], "keywords": [],
        }
