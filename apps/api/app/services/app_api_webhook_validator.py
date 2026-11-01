"""App API Webhook Validator — validate webhook configurations."""
from __future__ import annotations
from dataclasses import dataclass
import re
import structlog

log = structlog.get_logger()

_URL_RE = re.compile(r"^https://[^\s]+$")

@dataclass
class ValidationIssue:
    field: str
    message: str

class AppAPIWebhookValidator:
    def validate_config(self, url: str, events: list[str], secret: str = "") -> list[ValidationIssue]:
        issues: list[ValidationIssue] = []
        if not url:
            issues.append(ValidationIssue("url", "URL is required"))
        elif not _URL_RE.match(url):
            issues.append(ValidationIssue("url", "URL must be HTTPS"))
        if not events:
            issues.append(ValidationIssue("events", "At least one event required"))
        if secret and len(secret) < 16:
            issues.append(ValidationIssue("secret", "Secret must be at least 16 characters"))
        return issues
