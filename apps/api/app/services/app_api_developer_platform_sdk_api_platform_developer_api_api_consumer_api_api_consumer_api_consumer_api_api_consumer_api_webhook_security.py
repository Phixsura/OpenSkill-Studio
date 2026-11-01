"""Consumer API Webhook Security — manage webhook security policies."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class WebhookSecurityPolicy:
    webhook_id: str
    consumer_id: str
    require_https: bool = True
    require_signature: bool = True
    signature_algorithm: str = "sha256"
    ip_whitelist: list[str] = field(default_factory=list)
    max_payload_bytes: int = 1048576  # 1MB
    timeout_ms: int = 30000

@dataclass
class SecurityAuditResult:
    webhook_id: str
    score: int  # 0-100
    issues: list[str] = field(default_factory=list)
    compliant: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiWebhookSecurity:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str, str], WebhookSecurityPolicy] = {}

    def set_policy(self, installation_id: str, policy: WebhookSecurityPolicy) -> WebhookSecurityPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if policy.signature_algorithm not in ("sha256", "sha512"):
            raise ValueError(f"Unsupported algorithm: {policy.signature_algorithm}")
        if policy.max_payload_bytes < 1024:
            raise ValueError("max_payload_bytes must be at least 1KB")
        if policy.timeout_ms < 1000:
            raise ValueError("timeout_ms must be at least 1000")
        self._policies[(installation_id, policy.consumer_id, policy.webhook_id)] = policy
        return policy

    def audit(self, installation_id: str, consumer_id: str, webhook_id: str, url: str) -> SecurityAuditResult:
        key = (installation_id, consumer_id, webhook_id)
        policy = self._policies.get(key)
        issues: list[str] = []
        score = 100
        if not policy:
            return SecurityAuditResult(webhook_id=webhook_id, score=50, issues=["No security policy configured"], compliant=False)
        if policy.require_https and not url.startswith("https://"):
            issues.append("URL does not use HTTPS")
            score -= 30
        if not policy.require_signature:
            issues.append("Signature verification not required")
            score -= 20
        if not policy.ip_whitelist:
            issues.append("No IP whitelist configured")
            score -= 10
        if policy.max_payload_bytes > 5242880:
            issues.append("Payload limit exceeds 5MB")
            score -= 10
        if policy.timeout_ms > 60000:
            issues.append("Timeout exceeds 60 seconds")
            score -= 10
        return SecurityAuditResult(webhook_id=webhook_id, score=max(0, score), issues=issues, compliant=len(issues) == 0)

    def get_policy(self, installation_id: str, consumer_id: str, webhook_id: str) -> WebhookSecurityPolicy | None:
        return self._policies.get((installation_id, consumer_id, webhook_id))

    def list_policies(self, installation_id: str, consumer_id: str) -> list[WebhookSecurityPolicy]:
        return [p for (inst, cid, _), p in self._policies.items() if inst == installation_id and cid == consumer_id]
