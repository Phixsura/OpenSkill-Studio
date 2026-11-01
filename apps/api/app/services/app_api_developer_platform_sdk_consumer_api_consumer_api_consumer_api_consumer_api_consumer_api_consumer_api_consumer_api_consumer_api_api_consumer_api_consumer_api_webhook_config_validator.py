"""Consumer API Webhook Config Validator — validate webhook configurations."""
from __future__ import annotations
from dataclasses import dataclass, field
from urllib.parse import urlparse
import structlog

log = structlog.get_logger()

@dataclass
class WebhookConfig:
    webhook_id: str
    url: str
    secret: str = ""
    events: list[str] = field(default_factory=list)
    active: bool = True
    timeout_ms: int = 30000
    retry_count: int = 3

@dataclass
class ValidationIssue:
    field: str
    severity: str  # "error", "warning"
    message: str

@dataclass
class ConfigValidationResult:
    valid: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 100  # 0-100

class AppAPIDeveloperPlatformSDKConsumerApiWebhookConfigValidator:
    def __init__(self) -> None:
        pass

    def validate(self, config: WebhookConfig) -> ConfigValidationResult:
        issues: list[ValidationIssue] = []
        score = 100
        # URL validation
        parsed = urlparse(config.url)
        if not config.url:
            issues.append(ValidationIssue(field="url", severity="error", message="URL is required"))
            score -= 30
        elif parsed.scheme != "https":
            issues.append(ValidationIssue(field="url", severity="error", message="URL must use HTTPS"))
            score -= 25
        elif not parsed.hostname:
            issues.append(ValidationIssue(field="url", severity="error", message="URL must have a hostname"))
            score -= 25
        # Secret
        if not config.secret:
            issues.append(ValidationIssue(field="secret", severity="warning", message="No signing secret configured"))
            score -= 15
        elif len(config.secret) < 32:
            issues.append(ValidationIssue(field="secret", severity="warning", message="Secret should be at least 32 characters"))
            score -= 10
        # Events
        if not config.events:
            issues.append(ValidationIssue(field="events", severity="warning", message="No event filters — webhook receives all events"))
            score -= 5
        # Timeout
        if config.timeout_ms < 5000:
            issues.append(ValidationIssue(field="timeout_ms", severity="warning", message="Timeout below 5s may cause premature failures"))
            score -= 5
        elif config.timeout_ms > 60000:
            issues.append(ValidationIssue(field="timeout_ms", severity="warning", message="Timeout above 60s is excessive"))
            score -= 5
        # Retries
        if config.retry_count == 0:
            issues.append(ValidationIssue(field="retry_count", severity="warning", message="No retries configured"))
            score -= 10
        valid = not any(i.severity == "error" for i in issues)
        return ConfigValidationResult(valid=valid, issues=issues, score=max(0, score))
