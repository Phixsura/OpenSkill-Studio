"""Content Validator — validate extension content for marketplace compliance.

Scans extension metadata, descriptions, and assets for policy violations
including prohibited content, trademark issues, and quality standards.
"""
from __future__ import annotations
import re
from dataclasses import dataclass, field
from enum import Enum


class ViolationType(str, Enum):
    PROHIBITED_CONTENT = "prohibited_content"
    TRADEMARK = "trademark"
    MISLEADING = "misleading"
    QUALITY = "quality"
    SECURITY = "security"
    PRIVACY = "privacy"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ContentViolation:
    violation_type: ViolationType
    severity: Severity
    field: str
    message: str
    suggestion: str = ""


@dataclass
class ValidationReport:
    passed: bool
    violations: list[ContentViolation] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    score: int = 100


PROHIBITED_PATTERNS = [
    (re.compile(r"\b(hack|crack|pirat|warez)\b", re.I), ViolationType.PROHIBITED_CONTENT, Severity.HIGH),
    (re.compile(r"\b(password\s*steal|keylog\w*|spyware)\b", re.I), ViolationType.SECURITY, Severity.CRITICAL),
    (re.compile(r"\b(track\s*users?\s*without|collect\s*data\s*secretly)\b", re.I), ViolationType.PRIVACY, Severity.CRITICAL),
]

TRADEMARK_PATTERNS = [
    re.compile(r"\b(official\s+(?:google|microsoft|apple|amazon|meta))\b", re.I),
]

MISLEADING_PATTERNS = [
    (re.compile(r"\b(guaranteed|100%\s*(?:safe|secure|free))\b", re.I), "Avoid absolute claims"),
    (re.compile(r"#1\s+(?:app|extension|tool)", re.I), "Unverifiable ranking claim"),
]


class ContentValidatorService:
    """Validates extension content against marketplace policies."""

    def validate(self, content: dict) -> ValidationReport:
        violations: list[ContentViolation] = []
        warnings: list[str] = []

        # Validate each text field
        text_fields = {
            "name": content.get("name", ""),
            "description": content.get("description", ""),
            "short_description": content.get("short_description", ""),
            "changelog": content.get("changelog", ""),
        }

        for field_name, text in text_fields.items():
            if not text:
                continue
            # Prohibited content
            for pattern, vtype, severity in PROHIBITED_PATTERNS:
                if pattern.search(text):
                    violations.append(ContentViolation(
                        violation_type=vtype, severity=severity,
                        field=field_name,
                        message=f"Prohibited content detected in {field_name}",
                        suggestion="Remove or rephrase the flagged content",
                    ))

            # Trademark
            for pattern in TRADEMARK_PATTERNS:
                if pattern.search(text):
                    violations.append(ContentViolation(
                        violation_type=ViolationType.TRADEMARK, severity=Severity.MEDIUM,
                        field=field_name,
                        message=f"Potential trademark issue in {field_name}",
                        suggestion="Do not claim official affiliation with other companies",
                    ))

            # Misleading claims
            for pattern, suggestion in MISLEADING_PATTERNS:
                if pattern.search(text):
                    warnings.append(f"{field_name}: {suggestion}")

        # Quality checks
        name = content.get("name", "")
        if name and len(name) < 3:
            violations.append(ContentViolation(
                violation_type=ViolationType.QUALITY, severity=Severity.LOW,
                field="name", message="Name too short",
                suggestion="Use a descriptive name (3+ characters)",
            ))
        if name and name != name.strip():
            violations.append(ContentViolation(
                violation_type=ViolationType.QUALITY, severity=Severity.LOW,
                field="name", message="Name has leading/trailing whitespace",
            ))

        desc = content.get("description", "")
        if desc and len(desc) < 50:
            warnings.append("description: Consider a more detailed description (50+ chars)")

        # Calculate score
        score = 100
        for v in violations:
            if v.severity == Severity.CRITICAL:
                score -= 40
            elif v.severity == Severity.HIGH:
                score -= 20
            elif v.severity == Severity.MEDIUM:
                score -= 10
            else:
                score -= 5
        score = max(0, score)

        return ValidationReport(
            passed=not any(v.severity in (Severity.HIGH, Severity.CRITICAL) for v in violations),
            violations=violations, warnings=warnings, score=score,
        )
