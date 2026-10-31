"""Content Policy — enforce content guidelines for marketplace extensions.

Validates extension metadata (name, description, icons, screenshots)
against platform content policies before publishing.
"""
from __future__ import annotations
import re
from dataclasses import dataclass


@dataclass
class PolicyViolation:
    field: str
    rule: str
    message: str
    severity: str  # "error" or "warning"


class ContentPolicy:
    """Validates extension content against platform guidelines."""

    RESERVED_NAMES = {"openskill", "admin", "system", "api", "platform", "official"}
    MAX_NAME_LENGTH = 64
    MAX_DESCRIPTION_LENGTH = 2000
    MIN_DESCRIPTION_LENGTH = 20
    FORBIDDEN_PATTERNS = [
        (r"(?i)\b(free\s+money|get\s+rich|casino)\b", "Spam/scam language"),
        (r"(?i)\b(hack|crack|pirat)\b", "Prohibited content"),
    ]
    VALID_CATEGORIES = {
        "tools", "themes", "connectors", "analytics", "automation",
        "security", "testing", "documentation", "ui", "other",
    }

    def validate_name(self, name: str) -> list[PolicyViolation]:
        violations = []
        if not name.strip():
            violations.append(PolicyViolation("name", "required", "Name is required", "error"))
        elif len(name) > self.MAX_NAME_LENGTH:
            violations.append(PolicyViolation("name", "max_length",
                f"Name exceeds {self.MAX_NAME_LENGTH} characters", "error"))
        if name.lower().strip() in self.RESERVED_NAMES:
            violations.append(PolicyViolation("name", "reserved",
                f"'{name}' is a reserved name", "error"))
        return violations

    def validate_description(self, description: str) -> list[PolicyViolation]:
        violations = []
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            violations.append(PolicyViolation("description", "min_length",
                f"Description must be at least {self.MIN_DESCRIPTION_LENGTH} characters", "error"))
        if len(description) > self.MAX_DESCRIPTION_LENGTH:
            violations.append(PolicyViolation("description", "max_length",
                f"Description exceeds {self.MAX_DESCRIPTION_LENGTH} characters", "error"))
        for pattern, reason in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, description):
                violations.append(PolicyViolation("description", "forbidden_content",
                    f"Contains prohibited content: {reason}", "error"))
        return violations

    def validate_category(self, category: str) -> list[PolicyViolation]:
        if category not in self.VALID_CATEGORIES:
            return [PolicyViolation("category", "invalid",
                f"Invalid category. Must be one of: {', '.join(sorted(self.VALID_CATEGORIES))}", "error")]
        return []

    def validate_version(self, version: str) -> list[PolicyViolation]:
        if not re.match(r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?$", version):
            return [PolicyViolation("version", "format",
                "Version must follow semver format (e.g., 1.0.0)", "error")]
        return []

    def validate(self, metadata: dict) -> tuple[bool, list[PolicyViolation]]:
        """Run all validations on extension metadata."""
        violations = []
        violations.extend(self.validate_name(metadata.get("name", "")))
        violations.extend(self.validate_description(metadata.get("description", "")))
        if "category" in metadata:
            violations.extend(self.validate_category(metadata["category"]))
        if "version" in metadata:
            violations.extend(self.validate_version(metadata["version"]))
        errors = [v for v in violations if v.severity == "error"]
        return len(errors) == 0, violations
